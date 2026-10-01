"""FastAPI Dependency Injection providers."""

from functools import lru_cache
from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService
from RAG.services.rag_engine import RAGEngine


@lru_cache()
def get_ocr_orchestrator() -> OCROrchestratorService:
    """Dependency provider returning singleton OCROrchestratorService."""
    return OCROrchestratorService()


@lru_cache()
def get_rag_engine() -> RAGEngine:
    """Dependency provider returning singleton RAGEngine with indexed KB."""
    engine = RAGEngine()
    if engine.vector_store.count() == 0:
        engine.ingest_kb_documents()
    return engine
