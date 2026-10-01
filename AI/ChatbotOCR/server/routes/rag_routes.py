"""RAG routes placeholder (to be configured based on upcoming RAG guidance)."""

from fastapi import APIRouter
from pydantic import BaseModel

rag_router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])


class RAGStatusResponse(BaseModel):
    status: str = "initialized"
    message: str = "RAG module is ready for configuration."


@rag_router.get("/status", response_model=RAGStatusResponse)
def rag_status():
    """Placeholder health and readiness check for RAG subsystem."""
    return RAGStatusResponse()
