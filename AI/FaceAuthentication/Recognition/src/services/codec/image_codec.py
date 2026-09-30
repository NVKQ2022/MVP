"""
Image Codec Service: Handles image decoding, conversion, and encoding across
raw bytes, Base64 strings, file paths, and NumPy arrays.
"""

import base64
from io import BytesIO
from pathlib import Path
from typing import Union

import cv2
import numpy as np


class ImageCodecService:
    """
    Decodes diverse input payloads into OpenCV BGR numpy arrays,
    and encodes processed images back into Base64 or byte buffers.
    """

    @staticmethod
    def decode(image_input: Union[bytes, str, Path, np.ndarray, BytesIO]) -> np.ndarray:
        """
        Decodes any supported input format into a valid BGR numpy ndarray (H, W, 3).
        """
        if isinstance(image_input, np.ndarray):
            if image_input.ndim == 3 and image_input.shape[2] == 3:
                return image_input
            elif image_input.ndim == 2:
                return cv2.cvtColor(image_input, cv2.COLOR_GRAY2BGR)
            else:
                raise ValueError(f"Unsupported image array shape: {image_input.shape}")

        if isinstance(image_input, Path):
            if image_input.exists() and image_input.is_file():
                img = cv2.imread(str(image_input))
                if img is None:
                    raise ValueError(f"Failed to read image file at: {image_input}")
                return img
            raise FileNotFoundError(f"Image file does not exist: {image_input}")

        if isinstance(image_input, str):
            # If string is short, check if it's a valid local file path
            if len(image_input) < 1024:
                try:
                    path_obj = Path(image_input)
                    if path_obj.exists() and path_obj.is_file():
                        img = cv2.imread(str(path_obj))
                        if img is not None:
                            return img
                except (OSError, ValueError):
                    pass
            # Otherwise decode as base64 string
            return ImageCodecService.decode_base64(image_input)

        if isinstance(image_input, BytesIO):
            image_input = image_input.getvalue()

        if isinstance(image_input, bytes):
            return ImageCodecService.decode_bytes(image_input)

        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    @staticmethod
    def decode_bytes(image_bytes: bytes) -> np.ndarray:
        """Decodes raw image bytes into BGR numpy array."""
        if not image_bytes:
            raise ValueError("Empty image byte buffer received.")

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image bytes. Unsupported or corrupted format.")
        return img

    @staticmethod
    def decode_base64(base64_str: str) -> np.ndarray:
        """Decodes a base64 string or data URI into BGR numpy array."""
        clean_str = base64_str.strip()
        if "," in clean_str:
            clean_str = clean_str.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(clean_str)
        except Exception as e:
            raise ValueError(f"Invalid base64 encoding: {e}")

        return ImageCodecService.decode_bytes(image_bytes)

    @staticmethod
    def encode_to_base64(image_bgr: np.ndarray, format_ext: str = ".jpg") -> str:
        """Encodes a BGR numpy array to base64 string."""
        success, buffer = cv2.imencode(format_ext, image_bgr)
        if not success:
            raise ValueError("Failed to encode image to base64.")
        return base64.b64encode(buffer).decode("utf-8")

    @staticmethod
    def encode_to_bytes(image_bgr: np.ndarray, format_ext: str = ".jpg") -> bytes:
        """Encodes a BGR numpy array to image bytes."""
        success, buffer = cv2.imencode(format_ext, image_bgr)
        if not success:
            raise ValueError("Failed to encode image to bytes.")
        return buffer.tobytes()
