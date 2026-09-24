"""
Bounding Box Crop Preprocessing Service: Concrete implementation of BaseFacePreprocessingService
using direct bounding box cropping with margin padding.
"""

from typing import Tuple
import cv2
import numpy as np

from src.config import CROP_MARGIN_RATIO, NORM_MEAN, NORM_STD, TARGET_FACE_SIZE
from src.schemas.response_schemas import FaceDetectionDTO
from src.services.base.base_preprocessing import BaseFacePreprocessingService


class BBoxCropPreprocessingService(BaseFacePreprocessingService):
    """
    Preprocessing service applying bounding-box margin crop and normalization.
    Inherits from BaseFacePreprocessingService.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = TARGET_FACE_SIZE,
        margin_ratio: float = CROP_MARGIN_RATIO,
        norm_mean: float = NORM_MEAN,
        norm_std: float = NORM_STD,
    ):
        self._target_size = target_size
        self.margin_ratio = margin_ratio
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
        """Crops face using bounding box coordinates expanded with margin."""
        bbox = detection.bbox
        img_h, img_w = image_bgr.shape[:2]
        margin_w = int(bbox.width * self.margin_ratio)
        margin_h = int(bbox.height * self.margin_ratio)

        x1 = max(0, bbox.origin_x - margin_w)
        y1 = max(0, bbox.origin_y - margin_h)
        x2 = min(img_w, bbox.origin_x + bbox.width + margin_w)
        y2 = min(img_h, bbox.origin_y + bbox.height + margin_h)

        crop = image_bgr[y1:y2, x1:x2]
        if crop.size == 0:
            return cv2.resize(image_bgr, self._target_size, interpolation=cv2.INTER_AREA)

        interp = cv2.INTER_AREA if (crop.shape[1] > self._target_size[0]) else cv2.INTER_LINEAR
        return cv2.resize(crop, self._target_size, interpolation=interp)

    def normalize_tensor(self, face_bgr: np.ndarray) -> np.ndarray:
        """Converts BGR face to RGB, normalizes, and formats into (1, 3, H, W)."""
        h, w = face_bgr.shape[:2]
        if (w, h) != self._target_size:
            face_bgr = cv2.resize(face_bgr, self._target_size, interpolation=cv2.INTER_AREA)

        rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        blob = np.transpose(rgb, (2, 0, 1)).astype(np.float32)
        blob = (blob - self.norm_mean) / self.norm_std
        return np.expand_dims(blob, axis=0)
