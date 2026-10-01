"""Health and liveness probe routes."""

from fastapi import APIRouter, Depends
from server.config import server_settings
from server.dependencies import get_ocr_orchestrator
from OCR.schemas.response_schemas import HealthResponse
from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService

health_router = APIRouter(tags=["Health"])


@health_router.get("/health", response_model=HealthResponse)
def health_check(
    orchestrator: OCROrchestratorService = Depends(get_ocr_orchestrator),
) -> HealthResponse:
    """Liveness and readiness health probe."""
    info = orchestrator.get_service_info()
    return HealthResponse(
        status="healthy",
        app_name=server_settings.app_name,
        version=server_settings.app_version,
        backend=info.active_backend,
        device="GPU" if info.use_gpu else "CPU",
    )
