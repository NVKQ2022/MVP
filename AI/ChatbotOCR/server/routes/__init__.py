"""Server routes package."""

from server.routes.health_routes import health_router
from server.routes.ocr_routes import ocr_router
from server.routes.rag_routes import rag_router

__all__ = ["health_router", "ocr_router", "rag_router"]
