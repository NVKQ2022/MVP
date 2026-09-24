"""
Face preprocessor for ArcFace feature embedding model.
Performs resizing, color conversion (BGR -> RGB), normalization, and NCHW tensor formatting.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np

from src.config import NORM_MEAN, NORM_STD, TARGET_FACE_SIZE


class FacePreprocessor:
    """
    Preprocesses face images to the exact input format required by ArcFace embeddings models.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = TARGET_FACE_SIZE,
        norm_mean: float = NORM_MEAN,
        norm_std: float = NORM_STD,
    ):
        self.target_size = target_size
        self.norm_mean = float(norm_mean)
        self.norm_std = float(norm_std)

    def preprocess(self, image_bgr: np.ndarray) -> np.ndarray:
        """
        Preprocess a single BGR face image for ArcFace model inference.

        Args:
            image_bgr: numpy ndarray in BGR channel format.

        Returns:
            np.ndarray with shape (1, 3, target_h, target_w) and float32 dtype.
        """
        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("Invalid or empty image provided to preprocessor.")

        # 1. Resize if image is not already target size
        h, w = image_bgr.shape[:2]
        if (w, h) != self.target_size:
            interp = cv2.INTER_AREA if (w > self.target_size[0] or h > self.target_size[1]) else cv2.INTER_LINEAR
            resized = cv2.resize(image_bgr, self.target_size, interpolation=interp)
        else:
            resized = image_bgr

        # 2. Color conversion: BGR -> RGB
        img_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # 3. Transpose HWC (112, 112, 3) -> CHW (3, 112, 112)
        blob = np.transpose(img_rgb, (2, 0, 1)).astype(np.float32)

        # 4. Normalization: (pixel - mean) / std -> typically [-1.0, 1.0]
        blob = (blob - self.norm_mean) / self.norm_std

        # 5. Add Batch Dimension: (1, 3, 112, 112)
        tensor = np.expand_dims(blob, axis=0)
        return tensor

    def preprocess_batch(self, images_bgr: List[np.ndarray]) -> np.ndarray:
        """
        Preprocess a batch of BGR face images into a single NCHW tensor (N, 3, H, W).
        """
        if not images_bgr:
            raise ValueError("Empty image list provided to preprocess_batch.")

        tensors = [self.preprocess(img) for img in images_bgr]
        return np.concatenate(tensors, axis=0)

    def preprocess_file(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Loads an image from file and applies ArcFace preprocessing.
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found at {path}")

        img_bgr = cv2.imread(str(path))
        if img_bgr is None:
            raise ValueError(f"Could not decode image at {path}")

        return self.preprocess(img_bgr)
