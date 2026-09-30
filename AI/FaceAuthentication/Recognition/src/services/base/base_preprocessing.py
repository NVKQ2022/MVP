"""
Abstract Root Base Class for all Face Preprocessing and Alignment Services.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np

from src.schemas.response_schemas import FaceDetectionDTO


class BaseFacePreprocessingService(ABC):
    """
    Root Abstract Service for Face Cropping, Alignment, and Tensor Normalization.
    """

    @abstractmethod
    def align_and_crop(
        self,
        image_bgr: np.ndarray,
        detection: FaceDetectionDTO,
    ) -> np.ndarray:
        """
        Crops and geometry-aligns the face from raw image based on detection metadata.

        Args:
            image_bgr: Source OpenCV BGR numpy array (H, W, 3).
            detection: FaceDetectionDTO containing bounding box and keypoints.

        Returns:
            Aligned/Cropped BGR face image with shape (target_height, target_width, 3).
        """
        pass

    @abstractmethod
    def normalize_tensor(self, face_bgr: np.ndarray) -> np.ndarray:
        """
        Preprocesses and normalizes a cropped face into the exact model input tensor.

        Args:
            face_bgr: Cropped BGR face image.

        Returns:
            4D float32 numpy tensor with shape (1, channels, height, width).
        """
        pass

    def normalize_batch(self, faces_bgr: List[np.ndarray]) -> np.ndarray:
        """
        Preprocesses a batch of cropped face images into a single 4D tensor (N, C, H, W).
        Default implementation concatenates individual preprocessed tensors.
        """
        if not faces_bgr:
            raise ValueError("Empty face list passed to normalize_batch.")
        tensors = [self.normalize_tensor(f) for f in faces_bgr]
        return np.concatenate(tensors, axis=0)

    @property
    @abstractmethod
    def target_size(self) -> Tuple[int, int]:
        """Returns the target (width, height) resolution of the cropped face."""
        pass
