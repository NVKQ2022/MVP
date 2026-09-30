"""API package exporting FastAPI app and router."""

from src.api.app import app, create_app

__all__ = ["app", "create_app"]
