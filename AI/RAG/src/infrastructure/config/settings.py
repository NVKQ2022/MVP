"""Infrastructure settings and configuration loader."""

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> bool:
        return False

# Load .env file from project root or parent directories
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    endpoint: str = os.getenv("ENDPOINT", "").strip().strip('"').strip("'")
    provider: str = os.getenv("PROVIDER", "openai").strip().strip('"').strip("'")
    api_key: str = os.getenv("API_KEY", "").strip().strip('"').strip("'")
    model_name: str = (os.getenv("MODEL_NAME") or os.getenv("LLM_MODEL") or "").strip().strip('"').strip("'")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small").strip().strip('"').strip("'")
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "chroma_db").strip().strip('"').strip("'")
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "rfc_docs").strip().strip('"').strip("'")

    @classmethod
    def load(cls) -> "Settings":
        """Instantiate settings from current environment."""
        return cls()


# Default singleton instance
settings = Settings.load()

# Backward compatible module-level attributes
ENDPOINT = settings.endpoint
PROVIDER = settings.provider
API_KEY = settings.api_key
MODEL_NAME = settings.model_name
EMBEDDING_MODEL = settings.embedding_model
CHROMA_PERSIST_DIR = settings.chroma_persist_dir
CHROMA_COLLECTION = settings.chroma_collection
