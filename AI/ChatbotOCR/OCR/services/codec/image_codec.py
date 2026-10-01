"""Universal Image Codec Adapter for decoding and encoding various image formats."""

import base64
import re
from typing import Union, Optional
import cv2
import numpy as np
import requests

from OCR.utils.logger import get_logger

logger = get_logger(__name__)


class ImageCodecError(ValueError):
    """Exception raised for image decoding/encoding errors."""
    pass


class ImageCodecService:
    """Universal Codec Adapter Pattern.

    Converts incoming Base64, raw bytes, URLs, and uploaded files into canonical
    in-memory numpy arrays (BGR format, uint8), and encodes numpy arrays back to Base64.
    """

    @classmethod
    def decode(
        cls,
        payload: Union[str, bytes, np.ndarray],
        is_url: bool = False,
    ) -> np.ndarray:
        """Decodes raw input data into a 3-channel BGR numpy array.

        Args:
            payload: Base64 string, URL string, raw bytes, or existing numpy array.
            is_url: Whether the payload string should be treated as a remote URL.

        Returns:
            np.ndarray: Decoded image in BGR format (H, W, 3).
        """
        if isinstance(payload, np.ndarray):
            return cls.validate_and_normalize(payload)

        if isinstance(payload, bytes):
            return cls.decode_bytes(payload)

        if isinstance(payload, str):
            payload = payload.strip()
            if is_url or payload.startswith("http://") or payload.startswith("https://"):
                return cls.decode_url(payload)
            return cls.decode_base64(payload)

        raise ImageCodecError(f"Unsupported payload type: {type(payload)}")

    @classmethod
    def decode_base64(cls, base64_str: str) -> np.ndarray:
        """Decodes base64 string (with or without data URI scheme) to BGR numpy array."""
        if not base64_str:
            raise ImageCodecError("Base64 string is empty.")

        # Strip Data URI prefix e.g. "data:image/jpeg;base64,"
        if "," in base64_str and base64_str.startswith("data:"):
            base64_str = base64_str.split(",", 1)[1]

        # Clean whitespace and newlines
        clean_b64 = re.sub(r"\s+", "", base64_str)

        # Fix base64 padding if needed
        missing_padding = len(clean_b64) % 4
        if missing_padding:
            clean_b64 += "=" * (4 - missing_padding)

        try:
            image_bytes = base64.b64decode(clean_b64, validate=True)
        except Exception as e:
            raise ImageCodecError(f"Failed to decode base64 string: {str(e)}") from e

        return cls.decode_bytes(image_bytes)

    @classmethod
    def decode_bytes(cls, image_bytes: bytes) -> np.ndarray:
        """Decodes raw byte array to BGR numpy array."""
        if not image_bytes or len(image_bytes) == 0:
            raise ImageCodecError("Image byte buffer is empty.")

        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)

        if image is None:
            raise ImageCodecError("Failed to decode image from bytes. File may be corrupted or invalid format.")

        return cls.validate_and_normalize(image)

    @classmethod
    def decode_url(cls, url: str, timeout: float = 15.0) -> np.ndarray:
        """Downloads image from a remote URL and decodes into BGR numpy array."""
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            raise ImageCodecError(f"Invalid URL: '{url}'")

        try:
            logger.info(f"Downloading image from URL: {url}")
            headers = {"User-Agent": "Mozilla/5.0 (PaddleOCR-API/1.0)"}
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return cls.decode_bytes(response.content)
        except Exception as e:
            raise ImageCodecError(f"Failed to download image from URL '{url}': {str(e)}") from e

    @classmethod
    def encode_base64(
        cls,
        image: np.ndarray,
        extension: str = ".jpg",
        quality: int = 90,
    ) -> str:
        """Encodes an in-memory BGR numpy array into a base64 string."""
        if image is None or image.size == 0:
            raise ImageCodecError("Cannot encode empty image array.")

        params = []
        if extension.lower() in [".jpg", ".jpeg"]:
            params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        elif extension.lower() == ".png":
            params = [int(cv2.IMWRITE_PNG_COMPRESSION), 4]

        success, encoded_img = cv2.imencode(extension, image, params)
        if not success:
            raise ImageCodecError("Failed to encode image to base64 format.")

        b64_str = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
        mime = "image/jpeg" if extension.lower() in [".jpg", ".jpeg"] else "image/png"
        return f"data:{mime};base64,{b64_str}"

    @classmethod
    def validate_and_normalize(cls, image: np.ndarray) -> np.ndarray:
        """Validates image dimensions and converts grayscale / 4-channel RGBA to 3-channel BGR."""
        if not isinstance(image, np.ndarray):
            raise ImageCodecError(f"Expected numpy.ndarray, got {type(image)}")

        if image.size == 0 or len(image.shape) < 2:
            raise ImageCodecError("Invalid image array shape: image is empty or has < 2 dimensions.")

        h, w = image.shape[:2]
        if h < 4 or w < 4:
            raise ImageCodecError(f"Image dimensions too small ({w}x{h}). Minimum size is 4x4.")

        # Convert grayscale (H, W) -> (H, W, 3) BGR
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        # Convert RGBA / BGRA (H, W, 4) -> (H, W, 3) BGR
        elif len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        elif len(image.shape) == 3 and image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif len(image.shape) == 3 and image.shape[2] == 3:
            pass  # Already 3 channels
        else:
            raise ImageCodecError(f"Unsupported number of image channels: {image.shape}")

        return image
