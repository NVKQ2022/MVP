"""RAG service status and management routes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from RAG.services.rag_engine import RAGEngine
from server.dependencies import get_rag_engine

rag_router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])


class RAGStatusResponse(BaseModel):
    status: str = Field(default="ready", description="RAG subsystem operational status.")
    indexed_chunks: int = Field(default=0, description="Total indexed knowledge chunks in vector database.")
    collection_name: str = Field(default="", description="Active ChromaDB collection name.")
    embedding_model: str = Field(default="", description="Active embedding model name.")


@rag_router.get("/status", response_model=RAGStatusResponse)
def get_rag_status(engine: RAGEngine = Depends(get_rag_engine)) -> RAGStatusResponse:
    """Returns active knowledge base collection status, indexed document count, and embedding model."""
    return RAGStatusResponse(
        status="ready",
        indexed_chunks=engine.vector_store.count(),
        collection_name=engine.collection_name,
        embedding_model=engine.embedding_model_name,
    )
