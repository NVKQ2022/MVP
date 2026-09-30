"""
FastAPI Application initialization and service lifecycle management.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import API_TITLE, API_VERSION
from src.services.orchestrator import FaceRecognitionService


class AppState:
    """Holds global application state and singleton service instances."""
    recognition_service: FaceRecognitionService = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for service startup and teardown."""
    print(" Initializing Face Recognition Services...")
    app_state.recognition_service = FaceRecognitionService()
    print(" Services initialized and ready to receive requests.")
    yield
    print(" Shutting down Face Recognition Services...")
    if app_state.recognition_service is not None:
        app_state.recognition_service.close()


def create_app() -> FastAPI:
    """Factory creating and configuring the FastAPI app."""
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="High-Performance Face Detection (BlazeFace) & Recognition (ArcFace) API.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from src.api.routes import router
    app.include_router(router)

    return app


app = create_app()
