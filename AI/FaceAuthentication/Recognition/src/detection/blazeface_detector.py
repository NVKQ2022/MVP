"""
BlazeFace detector implementation wrapping MediaPipe Face Detection.
Provides clean face bounding box and 6-landmark facial keypoints extraction.
"""

import os
import sys
import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np

# Automatically load local libGLESv2 library if present (for headless Linux environments)
from src.config import BLAZEFACE_MODEL_PATH, DETECTION_CONFIDENCE_THRESHOLD, LIBS_DIR

lib_gles = LIBS_DIR / "libGLESv2.so.2"
if lib_gles.exists():
    try:
        ctypes.CDLL(str(lib_gles))
    except Exception:
        pass

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


@dataclass
class FaceDetection:
    """
    Represents a detected face instance.
    
    Coordinates:
        bbox: (xmin, ymin, width, height) in integer pixel coordinates.
        score: Confidence score [0.0, 1.0].
        keypoints: List of (x, y) landmark pixel coordinates:
            0: Right eye (subject's right eye, viewer's left)
            1: Left eye (subject's left eye, viewer's right)
            2: Nose tip
            3: Mouth center
            4: Right ear tragion
            5: Left ear tragion
        normalized_bbox: (xmin, ymin, width, height) in [0.0, 1.0].
        normalized_keypoints: List of (x, y) landmarks in [0.0, 1.0].
    """
    bbox: Tuple[int, int, int, int]
    score: float
    keypoints: List[Tuple[float, float]]
    normalized_bbox: Tuple[float, float, float, float]
    normalized_keypoints: List[Tuple[float, float]]

    @property
    def xmin(self) -> int:
        return self.bbox[0]

    @property
    def ymin(self) -> int:
        return self.bbox[1]

    @property
    def width(self) -> int:
        return self.bbox[2]

    @property
    def height(self) -> int:
        return self.bbox[3]

    @property
    def xmax(self) -> int:
        return self.bbox[0] + self.bbox[2]

    @property
    def ymax(self) -> int:
        return self.bbox[1] + self.bbox[3]


class BlazeFaceDetector:
    """
    BlazeFace detector wrapper using MediaPipe Vision Tasks API.
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        min_detection_confidence: float = DETECTION_CONFIDENCE_THRESHOLD,
    ):
        self.model_path = Path(model_path or BLAZEFACE_MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"BlazeFace model not found at '{self.model_path}'. "
                "Please run models download script or check config."
            )

        self.min_confidence = min_detection_confidence
        base_options = python.BaseOptions(model_asset_path=str(self.model_path))
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=self.min_confidence,
        )
        self._detector = vision.FaceDetector.create_from_options(options)

    def detect(self, image_input: Union[np.ndarray, str, Path]) -> List[FaceDetection]:
        """
        Detect faces in an image.

        Args:
            image_input: BGR image numpy array or filepath.

        Returns:
            List of FaceDetection objects sorted by confidence (descending).
        """
        if isinstance(image_input, (str, Path)):
            img_bgr = cv2.imread(str(image_input))
            if img_bgr is None:
                raise ValueError(f"Could not read image from {image_input}")
        elif isinstance(image_input, np.ndarray):
            img_bgr = image_input
        else:
            raise TypeError("image_input must be a numpy ndarray or file path")

        h, w = img_bgr.shape[:2]
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        results = self._detector.detect(mp_image)
        detections: List[FaceDetection] = []

        if not results or not results.detections:
            return detections

        for det in results.detections:
            score = float(det.categories[0].score) if det.categories else 0.0
            box = det.bounding_box

            # Absolute bounding box coords clamped to image boundaries
            xmin = max(0, int(box.origin_x))
            ymin = max(0, int(box.origin_y))
            box_w = int(box.width)
            box_h = int(box.height)

            # Keypoints
            abs_kps: List[Tuple[float, float]] = []
            norm_kps: List[Tuple[float, float]] = []
            for kp in det.keypoints:
                norm_kps.append((float(kp.x), float(kp.y)))
                abs_kps.append((float(kp.x * w), float(kp.y * h)))

            norm_box = (
                float(box.origin_x / w),
                float(box.origin_y / h),
                float(box.width / w),
                float(box.height / h),
            )

            detections.append(
                FaceDetection(
                    bbox=(xmin, ymin, box_w, box_h),
                    score=score,
                    keypoints=abs_kps,
                    normalized_bbox=norm_box,
                    normalized_keypoints=norm_kps,
                )
            )

        # Sort by detection score descending
        detections.sort(key=lambda d: d.score, reverse=True)
        return detections

    def detect_best(self, image_input: Union[np.ndarray, str, Path]) -> Optional[FaceDetection]:
        """
        Detect and return the single face with the highest confidence score.
        """
        detections = self.detect(image_input)
        return detections[0] if detections else None

    def close(self):
        """Release underlying detector resources."""
        if hasattr(self, "_detector") and self._detector is not None:
            try:
                self._detector.close()
            except Exception:
                pass
            self._detector = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
