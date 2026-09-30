"""
Abstract Root Base Class for all Face Anti-Spoofing (FAS) and Liveness Check Services.
Defines the standard contract that any liveness detection backend must satisfy.
"""

from abc import ABC, abstractmethod
import numpy as np

from src.schemas.response_schemas import BoundingBoxDTO, LivenessDTO


class BaseAntiSpoofingService(ABC):
    """
    Root Abstract Service for Face Anti-Spoofing / Liveness Check.
    Subclasses must implement `check_liveness` and `model_name`.
    """

    @abstractmethod
    def check_liveness(
        self,
        image_bgr: np.ndarray,
        bbox: BoundingBoxDTO,
    ) -> LivenessDTO:
        """
        Evaluates whether a detected face region is a live person or spoof attack (print/replay).

        Args:
            image_bgr: Source OpenCV BGR numpy array (H, W, 3).
            bbox: BoundingBoxDTO indicating the face location.

        Returns:
            LivenessDTO containing is_real, confidence, label, attack_type, and raw scores.
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the human-readable identifier of the anti-spoofing model backend."""
        pass

    def close(self) -> None:
        """Release underlying inference sessions or GPU resources. Default is no-op."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
