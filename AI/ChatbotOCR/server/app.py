from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server.config import server_settings
from server.routes import health_router, ocr_router, rag_router, pipeline_router
from server.dependencies import get_ocr_orchestrator, get_rag_engine
from OCR.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan handler."""
    logger.info(f"Starting {server_settings.app_name} v{server_settings.app_version}...")
    try:
        # Pre-warm OCR backend
        logger.info("Pre-warming OCR backend engine...")
        orchestrator = get_ocr_orchestrator()
        info = orchestrator.get_service_info()
        logger.info(
            f"OCR Backend '{info.active_backend}' warmed up successfully (Device: {'GPU' if info.use_gpu else 'CPU'})."
        )

        # Pre-warm RAG knowledge base
        logger.info("Pre-warming RAG engine and verifying knowledge base index...")
        rag_engine = get_rag_engine()
        logger.info(f"RAG Engine ready with {rag_engine.vector_store.count()} indexed chunks.")
    except Exception as e:
        logger.error(f"Failed to pre-warm backend engines: {e}", exc_info=True)

    yield

    logger.info("Shutting down ChatbotOCR API Service...")


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application instance."""
    app = FastAPI(
        title=server_settings.app_name,
        version=server_settings.app_version,
        description="Unified REST API server for OCR and RAG services.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=server_settings.allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(health_router)
    app.include_router(ocr_router)
    app.include_router(rag_router)
    app.include_router(pipeline_router)

    # Static Assets & Web UI Mounting
    static_dir = Path("server/static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    samples_dir = Path("data/sample_screenshots")
    if samples_dir.exists():
        app.mount("/sample-images", StaticFiles(directory=str(samples_dir)), name="sample_images")

    @app.get("/", tags=["UI"], include_in_schema=False)
    def serve_ui():
        """Serves the ChatbotOCR Web UI single-page application."""
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"status": "ok", "message": "ChatbotOCR API is running. UI file not found."}

    return app


# Root app instance for ASGI servers (uvicorn server.app:app)
app = create_app()
