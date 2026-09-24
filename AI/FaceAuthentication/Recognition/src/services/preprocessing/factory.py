"""
Preprocessing Service Factory: Creates concrete preprocessing service instances based on configuration.
"""

from typing import Dict, Optional, Type

from src.config import PREPROCESSING_TYPE
from src.services.base.base_preprocessing import BaseFacePreprocessingService
from src.services.preprocessing.bbox_crop_service import BBoxCropPreprocessingService
from src.services.preprocessing.landmark_align_service import (
    CanonicalLandmarkPreprocessingService,
)


class PreprocessingServiceFactory:
    """
    Factory creating instances of BaseFacePreprocessingService subclasses.
    Enables dynamic switching between alignment methods via configuration.
    """

    _registry: Dict[str, Type[BaseFacePreprocessingService]] = {
        "landmark_affine": CanonicalLandmarkPreprocessingService,
        "bbox_crop": BBoxCropPreprocessingService,
    }

    @classmethod
    def register(cls, name: str, service_cls: Type[BaseFacePreprocessingService]) -> None:
        """Registers a new preprocessing service class."""
        cls._registry[name.lower()] = service_cls

    @classmethod
    def create(
        cls,
        backend_name: Optional[str] = None,
        **kwargs,
    ) -> BaseFacePreprocessingService:
        """
        Creates and returns a concrete preprocessing service instance.

        Args:
            backend_name: Name of backend (defaults to config.PREPROCESSING_TYPE).
            **kwargs: Arguments passed to service constructor.
        """
        name = (backend_name or PREPROCESSING_TYPE).lower()
        if name not in cls._registry:
            supported = list(cls._registry.keys())
            raise ValueError(
                f"Unsupported preprocessing backend: '{name}'. Available backends: {supported}"
            )

        service_cls = cls._registry[name]
        return service_cls(**kwargs)

    @classmethod
    def list_available(cls) -> list:
        """Returns list of registered preprocessing backends."""
        return list(cls._registry.keys())
