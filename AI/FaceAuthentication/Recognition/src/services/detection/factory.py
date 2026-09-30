"""
Detection Service Factory: Creates concrete detection service instances based on configuration.
"""

from typing import Dict, Optional, Type

from src.config import DETECTION_BACKBONE
from src.services.base.base_detection import BaseFaceDetectionService
from src.services.detection.blazeface_service import BlazeFaceDetectionService


class DetectionServiceFactory:
    """
    Factory creating instances of BaseFaceDetectionService subclasses.
    Enables dynamic switching between detectors via configuration.
    """

    _registry: Dict[str, Type[BaseFaceDetectionService]] = {
        "blazeface": BlazeFaceDetectionService,
    }

    @classmethod
    def register(cls, name: str, service_cls: Type[BaseFaceDetectionService]) -> None:
        """Registers a new detection backend class."""
        cls._registry[name.lower()] = service_cls

    @classmethod
    def create(
        cls,
        backend_name: Optional[str] = None,
        **kwargs,
    ) -> BaseFaceDetectionService:
        """
        Creates and returns a concrete detection service instance.

        Args:
            backend_name: Name of backend (defaults to config.DETECTION_BACKBONE).
            **kwargs: Arguments passed to service constructor.
        """
        name = (backend_name or DETECTION_BACKBONE).lower()
        if name not in cls._registry:
            supported = list(cls._registry.keys())
            raise ValueError(
                f"Unsupported detection backend: '{name}'. Available backends: {supported}"
            )

        service_cls = cls._registry[name]
        return service_cls(**kwargs)

    @classmethod
    def list_available(cls) -> list:
        """Returns list of registered detection backends."""
        return list(cls._registry.keys())
