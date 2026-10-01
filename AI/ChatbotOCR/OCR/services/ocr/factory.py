"""Factory for creating swappable OCR backend instances."""

from typing import Dict, Type, List, Optional
from OCR.services.base.base_ocr import BaseOCRBackend
from OCR.services.ocr.paddle_backend import PaddleOCRBackend
from OCR.services.ocr.mock_backend import MockOCRBackend
from OCR.utils.logger import get_logger

logger = get_logger(__name__)


class OCRFactory:
    """Factory Method & Registry Pattern for OCR backends."""

    _registry: Dict[str, Type[BaseOCRBackend]] = {
        "paddle": PaddleOCRBackend,
        "paddleocr": PaddleOCRBackend,
        "mock": MockOCRBackend,
    }

    _singleton_instances: Dict[str, BaseOCRBackend] = {}

    @classmethod
    def register(cls, name: str, backend_cls: Type[BaseOCRBackend]) -> None:
        """Registers a new OCR backend class."""
        key = name.strip().lower()
        cls._registry[key] = backend_cls
        logger.info(f"Registered OCR backend '{key}' -> {backend_cls.__name__}")

    @classmethod
    def create(
        cls,
        backend_name: str = "paddle",
        singleton: bool = True,
        **kwargs,
    ) -> BaseOCRBackend:
        """Instantiates or retrieves the configured OCR backend.

        Args:
            backend_name: Identifier of backend ('paddle', 'mock').
            singleton: If True, caches and returns singleton instance.
            **kwargs: Extra parameters passed to backend constructor.

        Returns:
            BaseOCRBackend: Instantiated backend.
        """
        key = backend_name.strip().lower()
        if key not in cls._registry:
            supported = list(cls._registry.keys())
            raise ValueError(
                f"Unknown OCR backend: '{backend_name}'. Supported backends: {supported}"
            )

        if singleton:
            cache_key = f"{key}_{kwargs}"
            if cache_key not in cls._singleton_instances:
                logger.info(f"Instantiating new singleton OCR backend for '{key}'")
                cls._singleton_instances[cache_key] = cls._registry[key](**kwargs)
            return cls._singleton_instances[cache_key]

        return cls._registry[key](**kwargs)

    @classmethod
    def list_available(cls) -> List[str]:
        """Returns list of all registered backend keys."""
        return sorted(list(cls._registry.keys()))
