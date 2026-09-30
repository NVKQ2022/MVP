"""
Embedding Services Package exporting ArcFace embedding service and Factory.
"""

from src.services.embedding.arcface_service import ArcFaceEmbeddingService
from src.services.embedding.factory import EmbeddingServiceFactory

__all__ = [
    "ArcFaceEmbeddingService",
    "EmbeddingServiceFactory",
]
