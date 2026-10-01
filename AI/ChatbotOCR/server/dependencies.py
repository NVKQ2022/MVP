"""FastAPI Dependency Injection providers."""

from functools import lru_cache
from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService


@lru_cache()
def get_ocr_orchestrator() -> OCROrchestratorService:
    """Dependency provider returning singleton OCROrchestratorService."""
    return OCROrchestratorService()
