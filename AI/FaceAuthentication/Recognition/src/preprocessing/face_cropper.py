"""
Face cropper and landmark-based face aligner.
Extracts faces from raw images and writes them to the Face/ directory.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np

from src.config import (
    CROP_MARGIN_RATIO,
    FACE_DIR,
    TARGET_FACE_SIZE,
    USE_ALIGNMENT,
)
from src.detection.blazeface_detector import FaceDetection

# Standard ArcFace 112x112 canonical reference landmarks:
# [Right eye, Left eye, Nose tip, Mouth center]
ARCFACE_CANONICAL_LANDMARKS_4PT = np.array(
    [
        [38.2946, 51.6963],  # Right eye (subject's right / viewer's left)
        [73.5318, 51.6963],  # Left eye (subject's left / viewer's right)
        [56.0252, 71.7366],  # Nose tip
        [56.0252, 92.3655],  # Mouth center
    ],
    dtype=np.float32,
)


class FaceCropper:
    """
    Extracts, aligns, and crops face regions from raw input images.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = TARGET_FACE_SIZE,
        margin_ratio: float = CROP_MARGIN_RATIO,
        use_alignment: bool = USE_ALIGNMENT,
        output_base_dir: Optional[Union[str, Path]] = None,
    ):
        self.target_size = target_size
        self.margin_ratio = margin_ratio
        self.use_alignment = use_alignment
        self.output_base_dir = Path(output_base_dir or FACE_DIR)

    def align_face(
        self,
        image_bgr: np.ndarray,
        keypoints: List[Tuple[float, float]],
        target_size: Optional[Tuple[int, int]] = None,
    ) -> np.ndarray:
        """
        Aligns face using 4-point partial affine similarity transformation (rotation, translation, scale).
        
        Args:
            image_bgr: Source BGR image.
            keypoints: Facial keypoints from BlazeFace (at least 4 keypoints: right eye, left eye, nose, mouth).
            target_size: Output image dimension (width, height). Defaults to (112, 112).
            
        Returns:
            Aligned BGR face image with canonical geometry.
        """
        size = target_size or self.target_size
        if len(keypoints) < 4:
            # Fallback if keypoints are insufficient
            return cv2.resize(image_bgr, size, interpolation=cv2.INTER_AREA)

        dst_pts = np.array(keypoints[:4], dtype=np.float32)

        # Scale canonical template if target size is not 112x112
        if size == (112, 112):
            ref_pts = ARCFACE_CANONICAL_LANDMARKS_4PT
        else:
            scale_x = size[0] / 112.0
            scale_y = size[1] / 112.0
            ref_pts = ARCFACE_CANONICAL_LANDMARKS_4PT * np.array([scale_x, scale_y], dtype=np.float32)

        # Compute optimal similarity transform
        transform_matrix, inliers = cv2.estimateAffinePartial2D(dst_pts, ref_pts)
        if transform_matrix is None:
            return cv2.resize(image_bgr, size, interpolation=cv2.INTER_AREA)

        aligned_face = cv2.warpAffine(
            image_bgr,
            transform_matrix,
            size,
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )
        return aligned_face

    def crop_bbox(
        self,
        image_bgr: np.ndarray,
        bbox: Tuple[int, int, int, int],
        margin_ratio: Optional[float] = None,
        target_size: Optional[Tuple[int, int]] = None,
    ) -> np.ndarray:
        """
        Crops face region using bounding box with margin padding and resizes to target_size.
        """
        margin = self.margin_ratio if margin_ratio is None else margin_ratio
        xmin, ymin, w, h = bbox
        img_h, img_w = image_bgr.shape[:2]

        margin_w = int(w * margin)
        margin_h = int(h * margin)

        crop_x1 = max(0, xmin - margin_w)
        crop_y1 = max(0, ymin - margin_h)
        crop_x2 = min(img_w, xmin + w + margin_w)
        crop_y2 = min(img_h, ymin + h + margin_h)

        cropped = image_bgr[crop_y1:crop_y2, crop_x1:crop_x2]
        if cropped.size == 0:
            return cv2.resize(image_bgr, target_size or self.target_size, interpolation=cv2.INTER_AREA)

        size = target_size or self.target_size
        interp = cv2.INTER_AREA if (cropped.shape[1] > size[0] or cropped.shape[0] > size[1]) else cv2.INTER_LINEAR
        return cv2.resize(cropped, size, interpolation=interp)

    def extract_face(
        self,
        image_bgr: np.ndarray,
        detection: FaceDetection,
        use_alignment: Optional[bool] = None,
    ) -> np.ndarray:
        """
        Extracts face from image using alignment (preferred) or bounding box crop.
        """
        align = self.use_alignment if use_alignment is None else use_alignment
        if align and len(detection.keypoints) >= 4:
            return self.align_face(image_bgr, detection.keypoints, target_size=self.target_size)
        return self.crop_bbox(image_bgr, detection.bbox, target_size=self.target_size)

    def save_face(
        self,
        face_img: np.ndarray,
        person_name: str,
        filename: str,
        subfolder: Optional[str] = None,
    ) -> Path:
        """
        Saves cropped face image to output folder (Face/<person_name>/<filename>).
        """
        target_dir = self.output_base_dir / person_name
        if subfolder:
            target_dir = target_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        save_path = target_dir / filename
        cv2.imwrite(str(save_path), face_img)
        return save_path
