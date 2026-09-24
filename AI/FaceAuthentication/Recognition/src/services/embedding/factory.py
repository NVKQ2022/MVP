"""
Embedding Service Factory: Creates concrete embedding service instances based on configuration.
"""

from typing import Dict, Optional, Type

from src.config import EMBEDDING_BACKBONE
from src.services.base.base_embedding import BaseFaceEmbeddingService
from src.services.embedding.arcface_service import ArcFaceEmbeddingService


class EmbeddingServiceFactory:
    """
    Factory creating instances of BaseFaceEmbeddingService subclasses.
    Enables dynamic switching between feature extractor backends via configuration.
    """

    _registry: Dict[str, Type[BaseFaceEmbeddingService]] = {
        "arcface": ArcFaceEmbeddingService,
    }

    @classmethod
    def register(cls, name: str, service_cls: Type[BaseFaceEmbeddingService]) -> None:
        """Registers a new embedding backend class (e.g., AdaFace, FaceNet, CosFace)."""
        cls._registry[name.lower()] = service_cls

    @classmethod
    def create(
        cls,
        backend_name: Optional[str] = None,
        **kwargs,
    ) -> BaseFaceEmbeddingService:
        """
        Creates and returns a concrete embedding service instance.

        Args:
            backend_name: Name of backend (defaults to config.EMBEDDING_BACKBONE).
            **kwargs: Arguments passed to service constructor.
        """
        name = (backend_name or EMBEDDING_BACKBONE).lower()
        if name not in cls._registry:
            supported = list(cls._registry.keys())
            raise ValueError(
                f"Unsupported embedding backend: '{name}'. Available backends: {supported}"
            )

        service_cls = cls._registry[name]
        return service_cls(**kwargs)

    @classmethod
    def list_available(cls) -> list:
        """Returns list of registered embedding backends."""
        return list(cls._registry.keys())
