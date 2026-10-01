"""Server routes package."""

from server.routes.health_routes import health_router
from server.routes.ocr_routes import ocr_router
from server.routes.rag_routes import rag_router
from server.routes.pipeline_routes import pipeline_router

__all__ = ["health_router", "ocr_router", "rag_router", "pipeline_router"]
