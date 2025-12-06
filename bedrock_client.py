"""AWS Bedrock client for embeddings, generation, and reranking"""
import json
import boto3
from typing import List, Dict
import config


class BedrockClient:
    """Client for AWS Bedrock operations"""
    
    def __init__(self):
        # Build client config
        client_config = {
            'service_name': 'bedrock-runtime',
            'region_name': config.AWS_REGION,
            'aws_access_key_id': config.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': config.AWS_SECRET_ACCESS_KEY
        }
        
        # Add session token if available (for temporary credentials)
        if config.AWS_SESSION_TOKEN:
            client_config['aws_session_token'] = config.AWS_SESSION_TOKEN
        
        self.bedrock_runtime = boto3.client(**client_config)
        
        # Same for bedrock client
        client_config['service_name'] = 'bedrock'
        self.bedrock = boto3.client(**client_config)
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings using Amazon Titan"""
        try:
            body = json.dumps({
                "inputText": text[:8000]  # Titan limit
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=config.EMBEDDING_MODEL,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body.get('embedding', [])
        
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
    
    def generate_response(self, prompt: str, context: str, temperature: float = None) -> Dict:
        """Generate response using Claude with guardrails"""
        if temperature is None:
            temperature = config.TEMPERATURE
        
        # Build prompt with context
        full_prompt = self._build_prompt(prompt, context)
        
        # Apply guardrails
        if config.GUARDRAILS_ENABLED:
            full_prompt = self._apply_guardrails(full_prompt)
        
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": config.MAX_TOKENS,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=config.GENERATION_MODEL,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            
            return {
                'answer': response_body['content'][0]['text'],
                'model': config.GENERATION_MODEL,
                'stop_reason': response_body.get('stop_reason', 'unknown')
            }
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'answer': f"Error generating response: {str(e)}",
                'model': config.GENERATION_MODEL,
                'stop_reason': 'error'
            }
    
    def rerank_documents(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Rerank documents using Amazon Rerank"""
        if not documents:
            return []
        
        try:
            # Prepare documents for reranking
            doc_texts = []
            for doc in documents:
                text = doc.get('text', '')[:2000]  # Limit text length
                doc_texts.append({"textDocument": {"text": text}})
            
            body = json.dumps({
                "queries": [{"textQuery": {"text": query}}],
                "sources": doc_texts
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=config.RERANKING_MODEL,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract scores and rerank
            results = response_body.get('results', [])
            if results and len(results) > 0:
                scores = results[0].get('relevanceScores', [])
                
                # Combine documents with scores
                reranked = []
                for i, score in enumerate(scores):
                    if i < len(documents):
                        doc = documents[i].copy()
                        doc['rerank_score'] = score
                        reranked.append(doc)
                
                # Sort by rerank score
                reranked.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
                return reranked[:config.TOP_K_RERANK]
            
            return documents[:config.TOP_K_RERANK]
        
        except Exception as e:
            print(f"Error reranking documents: {e}")
            return documents[:config.TOP_K_RERANK]
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build prompt with context"""
        return f"""You are a helpful AI assistant. Answer the user's question based on the provided context.

Context:
{context}

Question: {query}

Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain relevant information, say "I don't have enough information to answer this question."
- Be concise and accurate
- Cite specific parts of the context when possible
- If answering in a non-English language, maintain that language throughout

Answer:"""
    
    def _apply_guardrails(self, prompt: str) -> str:
        """Apply content guardrails"""
        guardrail_prefix = """You must follow these safety guidelines:
- Do not generate harmful, offensive, or inappropriate content
- Do not provide medical, legal, or financial advice
- Stay factual and grounded in the provided context
- Refuse requests for personal information or sensitive data

"""
        return guardrail_prefix + prompt
