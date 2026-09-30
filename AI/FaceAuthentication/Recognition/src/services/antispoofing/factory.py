"""
Anti-Spoofing Service Factory: Creates concrete liveness detection service instances based on configuration.
"""

from typing import Dict, Optional, Type

from src.config import ANTISPOOFING_BACKBONE
from src.services.antispoofing.minifasnet_service import MiniFASNetAntiSpoofingService
from src.services.base.base_antispoofing import BaseAntiSpoofingService


class AntiSpoofingServiceFactory:
    """
    Factory creating instances of BaseAntiSpoofingService subclasses.
    Enables dynamic switching between anti-spoofing backends via configuration.
    """

    _registry: Dict[str, Type[BaseAntiSpoofingService]] = {
        "minifasnet": MiniFASNetAntiSpoofingService,
    }

    @classmethod
    def register(cls, name: str, service_cls: Type[BaseAntiSpoofingService]) -> None:
        """Registers a new anti-spoofing backend class."""
        cls._registry[name.lower()] = service_cls

    @classmethod
    def create(
        cls,
        backend_name: Optional[str] = None,
        **kwargs,
    ) -> BaseAntiSpoofingService:
        """
        Creates and returns a concrete anti-spoofing service instance.

        Args:
            backend_name: Name of backend (defaults to config.ANTISPOOFING_BACKBONE).
            **kwargs: Arguments passed to service constructor.
        """
        name = (backend_name or ANTISPOOFING_BACKBONE).lower()
        if name not in cls._registry:
            supported = list(cls._registry.keys())
            raise ValueError(
                f"Unsupported anti-spoofing backend: '{name}'. Available backends: {supported}"
            )

        service_cls = cls._registry[name]
        return service_cls(**kwargs)

    @classmethod
    def list_available(cls) -> list:
        """Returns list of registered anti-spoofing backends."""
        return list(cls._registry.keys())
