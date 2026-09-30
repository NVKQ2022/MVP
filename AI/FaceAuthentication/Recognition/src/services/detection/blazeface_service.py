"""
BlazeFace Detection Service: Concrete implementation of BaseFaceDetectionService
wrapping Google's MediaPipe BlazeFace short-range detector.
"""

import ctypes
from pathlib import Path
from typing import List, Optional, Union

import cv2
import numpy as np

from src.config import (
    BLAZEFACE_MODEL_PATH,
    DETECTION_CONFIDENCE_THRESHOLD,
    LIBS_DIR,
)
from src.schemas.response_schemas import (
    BoundingBoxDTO,
    FaceDetectionDTO,
    KeypointDTO,
)
from src.services.base.base_detection import BaseFaceDetectionService
from src.services.codec.image_codec import ImageCodecService

# Auto-preload libGLESv2 for headless environments if available
lib_gles = LIBS_DIR / "libGLESv2.so.2"
if lib_gles.exists():
    try:
        ctypes.CDLL(str(lib_gles))
    except Exception:
        pass

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

LANDMARK_NAMES = [
    "right_eye",
    "left_eye",
    "nose_tip",
    "mouth_center",
    "right_ear_tragion",
    "left_ear_tragion",
]


class BlazeFaceDetectionService(BaseFaceDetectionService):
    """
    MediaPipe BlazeFace Face Detection Service.
    Inherits from BaseFaceDetectionService.
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        min_confidence: float = DETECTION_CONFIDENCE_THRESHOLD,
    ):
        self.model_path = Path(model_path or BLAZEFACE_MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"BlazeFace model not found at {self.model_path}. "
                "Run models/download_models.py to download."
            )

        self.min_confidence = min_confidence
        base_options = python.BaseOptions(model_asset_path=str(self.model_path))
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=self.min_confidence,
        )
        self._detector = vision.FaceDetector.create_from_options(options)

    @property
    def model_name(self) -> str:
        return "MediaPipe BlazeFace Short-Range"

    def detect(self, image_input: Union[bytes, str, Path, np.ndarray]) -> List[FaceDetectionDTO]:
        """Detects faces and outputs structured FaceDetectionDTO instances."""
        img_bgr = ImageCodecService.decode(image_input)
        h, w = img_bgr.shape[:2]

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        results = self._detector.detect(mp_image)
        if not results or not results.detections:
            return []

        face_dtos: List[FaceDetectionDTO] = []
        for det in results.detections:
            score = float(det.categories[0].score) if det.categories else 0.0
            box = det.bounding_box

            bbox_dto = BoundingBoxDTO(
                origin_x=max(0, int(box.origin_x)),
                origin_y=max(0, int(box.origin_y)),
                width=int(box.width),
                height=int(box.height),
            )

            keypoint_dtos: List[KeypointDTO] = []
            for i, kp in enumerate(det.keypoints):
                name = LANDMARK_NAMES[i] if i < len(LANDMARK_NAMES) else f"point_{i}"
                keypoint_dtos.append(
                    KeypointDTO(
                        name=name,
                        x=float(kp.x * w),
                        y=float(kp.y * h),
                    )
                )

            face_dtos.append(
                FaceDetectionDTO(
                    bbox=bbox_dto,
                    confidence=score,
                    keypoints=keypoint_dtos,
                )
            )

        face_dtos.sort(key=lambda d: d.confidence, reverse=True)
        return face_dtos

    def close(self) -> None:
        """Closes detector resources."""
        if hasattr(self, "_detector") and self._detector is not None:
            try:
                self._detector.close()
            except Exception:
                pass
            self._detector = None
