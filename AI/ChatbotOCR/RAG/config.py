"""Configuration for RAG module using environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env from project root if available
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class RAGSettings(BaseModel):
    """RAG configuration loaded from environment or sensible defaults."""

    rag_enabled: bool = Field(
        default_factory=lambda: os.getenv("RAG_ENABLED", "true").lower() in ("true", "1", "yes")
    )

    # LLM Settings
    openai_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_base_url: str | None = Field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL", None)
    )
    model_name: str = Field(
        default_factory=lambda: os.getenv("MODEL_NAME", "gpt-4o-mini")
    )

    # Embedding Settings
    embedding_model: str = Field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )

    # Vector Store Settings
    vector_store_type: str = Field(
        default_factory=lambda: os.getenv("VECTOR_STORE_TYPE", "milvus_lite").lower()
    )
    milvus_db_path: str = Field(
        default_factory=lambda: os.getenv("MILVUS_DB_PATH", "./data/milvus_lite.db")
    )
    milvus_collection_name: str = Field(
        default_factory=lambda: os.getenv("MILVUS_COLLECTION_NAME", "support_kb")
    )

    # ChromaDB Vector Store (retained for backward compatibility)
    chroma_persist_dir: str = Field(
        default_factory=lambda: os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
    )
    chroma_collection_name: str = Field(
        default_factory=lambda: os.getenv("CHROMA_COLLECTION_NAME", "support_kb")
    )

    # Knowledge Base Documents directory (sole source of truth)
    kb_docs_dir: str = Field(
        default_factory=lambda: os.getenv("KB_DOCS_DIR", str(ROOT_DIR / "data" / "kb_documents"))
    )

    # Chunking
    chunk_size: int = 1500
    chunk_overlap: int = 0
    top_k: int = 3


rag_settings = RAGSettings()
