"""Configuration for RAG Application"""
import os
from dotenv import load_dotenv

load_dotenv()

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    # Use Streamlit secrets if available (for cloud deployment)
    AWS_REGION = st.secrets.get("AWS_DEFAULT_REGION", "us-west-2")
    AWS_ACCESS_KEY_ID = st.secrets.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = st.secrets.get("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN = st.secrets.get("AWS_SESSION_TOKEN", None)
except:
    # Fall back to environment variables (for local development)
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")  # For temporary credentials

# Bedrock Models
GENERATION_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
RERANKING_MODEL = "amazon.rerank-v1:0"

VALID_GENERATION_MODELS = ["anthropic.claude-3-5-sonnet-20240620-v1:0"]
VALID_RERANKING_MODELS = ["amazon.rerank-v1:0"]

# Chunking Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MIN_CHUNK_SIZE = 100

# Retrieval Configuration
TOP_K_RETRIEVAL = 15  # Retrieve more chunks
TOP_K_RERANK = 7  # Rerank more results
SIMILARITY_THRESHOLD = 0.1  # Very low threshold for more inclusive retrieval

# Guardrails
GUARDRAILS_ENABLED = True
MAX_TOKENS = 4096
TEMPERATURE = 0.5  # Lower temperature for more focused answers

# File Support
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt', '.pptx', '.xlsx', '.csv']

# Storage
VECTOR_STORE_PATH = "./vector_store"
UPLOAD_FOLDER = "./uploaded_documents"

os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
