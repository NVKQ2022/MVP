"""
Abstract Root Base Class for all Face Detection Services.
Defines the standard contract that any detection backend must satisfy.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union

import numpy as np

from src.schemas.response_schemas import FaceDetectionDTO


class BaseFaceDetectionService(ABC):
    """
    Root Abstract Service for Face Detection.
    Subclasses must implement `detect` and `model_name`.
    """

    @abstractmethod
    def detect(self, image_input: Union[bytes, str, Path, np.ndarray]) -> List[FaceDetectionDTO]:
        """
        Detects all faces in the provided image payload.

        Args:
            image_input: Raw image bytes, Base64 string, local file Path, or OpenCV BGR numpy array.

        Returns:
            List of FaceDetectionDTO objects sorted by confidence descending.
        """
        pass

    def detect_best(self, image_input: Union[bytes, str, Path, np.ndarray]) -> Optional[FaceDetectionDTO]:
        """
        Returns the single face detection with the highest confidence score.
        Default implementation delegates to `detect` and picks the top element.
        """
        detections = self.detect(image_input)
        return detections[0] if detections else None

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the human-readable identifier of the detection model backend."""
        pass

    def close(self) -> None:
        """Release underlying system or GPU resources. Default is no-op."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
