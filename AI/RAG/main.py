"""Application composition and factory methods.

Wires Clean Architecture components via container.
"""

from typing import Any
from openai import OpenAI

from chunking import ChunkingService
from config import (
    API_KEY,
    CHROMA_COLLECTION,
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    ENDPOINT,
    MODEL_NAME,
    PROVIDER,
)
from embedding import EmbeddingService
from rag_service import RAGService
from src.container import default_container
from vectordb import ChromaVectorDB, VectorDB


def build_llm_client() -> OpenAI:
    """Build standard OpenAI client instance."""
    return OpenAI(
        base_url=ENDPOINT or None,
        api_key=API_KEY or None,
    )


def build_chunking_service() -> ChunkingService:
    """Build document chunking service."""
    return default_container.build_chunker(
        chunk_size=550,
        overlap=35,
        drop_empty=True,
    )


def build_embedding_service() -> EmbeddingService:
    """Build embedding service."""
    return default_container.build_embedding_model()


def build_vector_db(
    persist_directory: str | None = None,
    collection_name: str | None = None,
) -> VectorDB:
    """Build Chroma vector database."""
    return ChromaVectorDB(
        persist_directory=(
            persist_directory if persist_directory is not None else CHROMA_PERSIST_DIR
        ),
        collection_name=(
            collection_name if collection_name is not None else CHROMA_COLLECTION
        ),
    )


def build_rag_service() -> RAGService:
    """Build end-to-end RAG service."""
    client = build_llm_client()
    chunking_service = build_chunking_service()
    embedding_service = build_embedding_service()
    vector_db = build_vector_db()

    return RAGService(
        client=client,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        vector_db=vector_db,
        model_name=MODEL_NAME,
    )


def main():
    rag_service = build_rag_service()
    response = rag_service.query("What is the capital of France?")
    print(f"answer: {response['answer']}")


if __name__ == "__main__":
    main()
