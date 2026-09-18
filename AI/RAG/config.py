import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> bool:
        return False

load_dotenv()

ENDPOINT = os.getenv("ENDPOINT", "").strip().strip('"').strip("'")
PROVIDER = os.getenv("PROVIDER", "openai").strip().strip('"').strip("'")
API_KEY = os.getenv("API_KEY", "").strip().strip('"').strip("'")
MODEL_NAME = (os.getenv("MODEL_NAME") or os.getenv("LLM_MODEL") or "").strip().strip('"').strip("'")

# Embeddings: now local Sentence-Transformers
#EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2").strip().strip('"').strip("'")
# Embeddings: use openai text-embedding-3-small (or text-embedding-3-large) for cloud-based embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small").strip().strip('"').strip("'")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "rfc_docs")
