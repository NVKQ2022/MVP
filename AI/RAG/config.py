from dotenv import load_dotenv
import os

load_dotenv()

ENDPOINT = os.getenv("ENDPOINT", "").strip().strip('"').strip("'")
API_KEY = os.getenv("API_KEY", "").strip().strip('"').strip("'")
MODEL_NAME = (os.getenv("MODEL_NAME") or os.getenv("LLM_MODEL") or "").strip().strip('"').strip("'")

# Embeddings: now local Sentence-Transformers
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2").strip().strip('"').strip("'")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "rfc_docs")
