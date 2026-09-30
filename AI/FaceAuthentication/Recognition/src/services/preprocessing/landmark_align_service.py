"""
Canonical Landmark Preprocessing Service: Concrete implementation of BaseFacePreprocessingService
using 4-point partial affine similarity transformation to ArcFace canonical coordinates.
"""

from typing import List, Optional, Tuple

import cv2
import numpy as np

from src.config import NORM_MEAN, NORM_STD, TARGET_FACE_SIZE
from src.schemas.response_schemas import FaceDetectionDTO
from src.services.base.base_preprocessing import BaseFacePreprocessingService

# Canonical ArcFace 112x112 Landmark Reference:
# [Right Eye, Left Eye, Nose Tip, Mouth Center]
CANONICAL_LANDMARKS_4PT = np.array(
    [
        [38.2946, 51.6963],  # Right Eye (viewer's left)
        [73.5318, 51.6963],  # Left Eye (viewer's right)
        [56.0252, 71.7366],  # Nose Tip
        [56.0252, 92.3655],  # Mouth Center
    ],
    dtype=np.float32,
)


class CanonicalLandmarkPreprocessingService(BaseFacePreprocessingService):
    """
    Preprocessing service applying 4-point canonical affine alignment and ArcFace normalization.
    Inherits from BaseFacePreprocessingService.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = TARGET_FACE_SIZE,
        norm_mean: float = NORM_MEAN,
        norm_std: float = NORM_STD,
    ):
        self._target_size = target_size
        self.norm_mean = norm_mean
        self.norm_std = norm_std

    @property
    def target_size(self) -> Tuple[int, int]:
        return self._target_size

    def align_and_crop(
        self,
        image_bgr: np.ndarray,
        detection: FaceDetectionDTO,
    ) -> np.ndarray:
        """Aligns face using 4-point partial affine similarity transformation."""
        keypoints = detection.keypoints
        if len(keypoints) < 4:
            # Fallback to direct resize if keypoints are insufficient
            return cv2.resize(image_bgr, self._target_size, interpolation=cv2.INTER_AREA)

        pts = np.array([[kp.x, kp.y] for kp in keypoints[:4]], dtype=np.float32)

        if self._target_size == (112, 112):
            ref_pts = CANONICAL_LANDMARKS_4PT
        else:
            scale_x = self._target_size[0] / 112.0
            scale_y = self._target_size[1] / 112.0
            ref_pts = CANONICAL_LANDMARKS_4PT * np.array([scale_x, scale_y], dtype=np.float32)

        transform_matrix, _ = cv2.estimateAffinePartial2D(pts, ref_pts)
        if transform_matrix is None:
            return cv2.resize(image_bgr, self._target_size, interpolation=cv2.INTER_AREA)

        aligned = cv2.warpAffine(
            image_bgr,
            transform_matrix,
            self._target_size,
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )
        return aligned

    def normalize_tensor(self, face_bgr: np.ndarray) -> np.ndarray:
        """
        Converts BGR face to RGB, normalizes pixel values: (x - mean) / std,
        and formats into (1, 3, H, W) NCHW float32 tensor.
        """
        h, w = face_bgr.shape[:2]
        if (w, h) != self._target_size:
            face_bgr = cv2.resize(face_bgr, self._target_size, interpolation=cv2.INTER_AREA)

        rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        blob = np.transpose(rgb, (2, 0, 1)).astype(np.float32)
        blob = (blob - self.norm_mean) / self.norm_std
        return np.expand_dims(blob, axis=0)
