"""
Image I/O and visualization utilities.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np

from src.schemas.response_schemas import FaceDetectionDTO

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images(directory: Union[str, Path], recursive: bool = True) -> List[Path]:
    """
    Finds all valid image files in a directory.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    pattern = "**/*" if recursive else "*"
    images = [
        p for p in dir_path.glob(pattern)
        if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    return sorted(images)


def load_image(image_path: Union[str, Path]) -> np.ndarray:
    """
    Loads an image from file and validates its readability.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at {path}")

    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Failed to read image at {path}")
    return img


def save_image(save_path: Union[str, Path], image: np.ndarray) -> Path:
    """
    Saves an image to disk, creating parent directories if necessary.
    """
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image)
    return path


def draw_detection(
    image: np.ndarray,
    detection: FaceDetectionDTO,
    color: Tuple[int, int, int] = (0, 255, 0),
    landmark_color: Tuple[int, int, int] = (0, 0, 255),
    thickness: int = 2,
) -> np.ndarray:
    """
    Draws bounding box, confidence score, and landmark keypoints on an image copy.
    """
    annotated = image.copy()
    bbox = detection.bbox
    xmin = bbox.origin_x
    ymin = bbox.origin_y
    w = bbox.width
    h = bbox.height

    # Bounding box
    cv2.rectangle(annotated, (xmin, ymin), (xmin + w, ymin + h), color, thickness)

    # Score label
    label = f"{detection.confidence:.2f}"
    cv2.putText(
        annotated,
        label,
        (xmin, max(20, ymin - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2,
        cv2.LINE_AA,
    )

    # Keypoints
    for kp in detection.keypoints:
        cv2.circle(annotated, (int(kp.x), int(kp.y)), 4, landmark_color, -1)

    return annotated
