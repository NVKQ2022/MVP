"""Base abstract interface for OCR backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class RawOCRItem:
    """Raw OCR detection item produced by a backend."""

    text: str
    confidence: float
    polygon: List[List[int]]
    box_2d: List[int]


class BaseOCRBackend(ABC):
    """Abstract Base Class (Strategy Pattern) defining the contract for OCR engine implementations."""

    @abstractmethod
    def predict(
        self,
        image: np.ndarray,
        lang: Optional[str] = None,
        det: bool = True,
        rec: bool = True,
        cls: bool = True,
    ) -> List[RawOCRItem]:
        """Runs OCR inference on an in-memory BGR/RGB numpy image.

        Args:
            image: Image as numpy array (H, W, C) in BGR format.
            lang: Optional language code to override default.
            det: Whether to perform text detection.
            rec: Whether to perform text recognition.
            cls: Whether to perform angle classification.

        Returns:
            List of RawOCRItem instances.
        """
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Human-readable identifier of this backend."""
        pass

    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """List of supported language codes."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Checks if the backend is initialized and ready for inference."""
        pass
