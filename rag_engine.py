"""RAG Engine - Orchestrates the entire RAG pipeline"""
import os
from typing import List, Dict
from document_processor import DocumentProcessor, SemanticChunker
from bedrock_client import BedrockClient
from vector_store import VectorStore
import config


class RAGEngine:
    """Complete RAG pipeline with semantic chunking and reranking"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.chunker = SemanticChunker(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            min_chunk_size=config.MIN_CHUNK_SIZE
        )
        self.bedrock = BedrockClient()
        self.vector_store = VectorStore()
    
    def ingest_document(self, file_path: str) -> Dict:
        """Ingest a document into the RAG system"""
        try:
            # Process document
            doc_data = self.doc_processor.process_document(file_path)
            
            # Create semantic chunks
            chunks = self.chunker.chunk_text(
                doc_data['text'],
                metadata={
                    'filename': doc_data['filename'],
                    'file_type': doc_data['file_type']
                }
            )
            
            if not chunks:
                return {
                    'success': False,
                    'message': 'No chunks created from document',
                    'chunks_created': 0
                }
            
            # Generate embeddings for each chunk
            embeddings = []
            for chunk in chunks:
                embedding = self.bedrock.generate_embeddings(chunk['text'])
                if embedding:
                    embeddings.append(embedding)
                else:
                    # Use zero vector if embedding fails
                    embeddings.append([0.0] * 1024)
            
            # Add to vector store
            self.vector_store.add_documents(chunks, embeddings)
            
            # Save vector store
            self.vector_store.save()
            
            return {
                'success': True,
                'message': f'Successfully ingested {doc_data["filename"]}',
                'chunks_created': len(chunks),
                'filename': doc_data['filename'],
                'char_count': doc_data['char_count'],
                'word_count': doc_data['word_count']
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error ingesting document: {str(e)}',
                'chunks_created': 0
            }
    
    def query(self, question: str, use_reranking: bool = True) -> Dict:
        """Query the RAG system"""
        try:
            # Check if we have documents
            stats = self.vector_store.get_stats()
            print(f"Vector store has {stats['total_documents']} documents")
            
            if stats['total_documents'] == 0:
                return {
                    'answer': 'No documents in vector store. Please upload and process documents first.',
                    'sources': [],
                    'error': False
                }
            
            # Generate query embedding
            print(f"Generating embedding for query: {question[:50]}...")
            query_embedding = self.bedrock.generate_embeddings(question)
            
            if not query_embedding:
                return {
                    'answer': 'Error generating query embedding. Check AWS credentials.',
                    'sources': [],
                    'error': True
                }
            
            print(f"Generated embedding with {len(query_embedding)} dimensions")
            
            # Retrieve relevant documents
            retrieved_docs = self.vector_store.search(
                query_embedding,
                top_k=config.TOP_K_RETRIEVAL
            )
            
            print(f"Retrieved {len(retrieved_docs)} documents from vector store")
            
            if not retrieved_docs:
                return {
                    'answer': f'No relevant documents found above similarity threshold ({config.SIMILARITY_THRESHOLD}). Try uploading more relevant documents or lowering the threshold.',
                    'sources': [],
                    'error': False
                }
            
            # Rerank documents
            if use_reranking and len(retrieved_docs) > 1:
                reranked_docs = self.bedrock.rerank_documents(question, retrieved_docs)
            else:
                reranked_docs = retrieved_docs[:config.TOP_K_RERANK]
            
            # Build context from top documents
            context = self._build_context(reranked_docs)
            
            # Generate response
            response = self.bedrock.generate_response(question, context)
            
            # Prepare sources
            sources = []
            for i, doc in enumerate(reranked_docs):
                sources.append({
                    'rank': i + 1,
                    'text': doc['text'][:300] + '...' if len(doc['text']) > 300 else doc['text'],
                    'filename': doc.get('filename', 'Unknown'),
                    'chunk_id': doc.get('chunk_id', 0),
                    'similarity_score': doc.get('similarity_score', 0),
                    'rerank_score': doc.get('rerank_score', 0)
                })
            
            return {
                'answer': response['answer'],
                'sources': sources,
                'model': response['model'],
                'num_sources': len(sources),
                'error': False
            }
        
        except Exception as e:
            return {
                'answer': f'Error processing query: {str(e)}',
                'sources': [],
                'error': True
            }
    
    def _build_context(self, documents: List[Dict]) -> str:
        """Build context string from documents"""
        context_parts = []
        
        for i, doc in enumerate(documents):
            context_parts.append(
                f"[Source {i+1} - {doc.get('filename', 'Unknown')}]\n{doc['text']}"
            )
        
        return "\n\n".join(context_parts)
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        vector_stats = self.vector_store.get_stats()
        
        return {
            'total_documents': vector_stats['total_documents'],
            'vector_dimension': vector_stats['dimension'],
            'chunk_size': config.CHUNK_SIZE,
            'chunk_overlap': config.CHUNK_OVERLAP,
            'top_k_retrieval': config.TOP_K_RETRIEVAL,
            'top_k_rerank': config.TOP_K_RERANK,
            'generation_model': config.GENERATION_MODEL,
            'reranking_model': config.RERANKING_MODEL,
            'guardrails_enabled': config.GUARDRAILS_ENABLED
        }
    
    def clear_all(self):
        """Clear all documents from the system"""
        self.vector_store.clear()
