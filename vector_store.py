"""Vector store using FAISS for efficient similarity search"""
import os
import pickle
import numpy as np
import faiss
from typing import List, Dict
import config


class VectorStore:
    """FAISS-based vector store for document embeddings"""
    
    def __init__(self):
        self.index = None
        self.documents = []
        self.dimension = 1024  # Titan embeddings dimension
        self.index_path = os.path.join(config.VECTOR_STORE_PATH, "faiss_index.bin")
        self.docs_path = os.path.join(config.VECTOR_STORE_PATH, "documents.pkl")
        
        # Load existing index if available
        self.load()
    
    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """Add documents with their embeddings to the vector store"""
        if not documents or not embeddings:
            return
        
        # Initialize index if needed
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_array)
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store documents
        self.documents.extend(documents)
        
        print(f"Added {len(documents)} documents. Total: {len(self.documents)}")
    
    def search(self, query_embedding: List[float], top_k: int = None) -> List[Dict]:
        """Search for similar documents"""
        if self.index is None or len(self.documents) == 0:
            return []
        
        if top_k is None:
            top_k = config.TOP_K_RETRIEVAL
        
        # Normalize query embedding
        query_array = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_array)
        
        # Search
        top_k = min(top_k, len(self.documents))
        distances, indices = self.index.search(query_array, top_k)
        
        # Retrieve documents with scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['similarity_score'] = float(distances[0][i])
                
                # Filter by threshold
                if doc['similarity_score'] >= config.SIMILARITY_THRESHOLD:
                    results.append(doc)
        
        return results
    
    def save(self):
        """Save index and documents to disk"""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            print(f"Saved FAISS index to {self.index_path}")
        
        if self.documents:
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            print(f"Saved {len(self.documents)} documents to {self.docs_path}")
    
    def load(self):
        """Load index and documents from disk"""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            print(f"Loaded FAISS index from {self.index_path}")
        
        if os.path.exists(self.docs_path):
            with open(self.docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            print(f"Loaded {len(self.documents)} documents from {self.docs_path}")
    
    def clear(self):
        """Clear all documents and index"""
        self.index = None
        self.documents = []
        
        # Remove files
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.docs_path):
            os.remove(self.docs_path)
        
        print("Cleared vector store")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0,
            'dimension': self.dimension
        }
