"""Tests for ImageCodecService."""

import pytest
import numpy as np
import cv2

from OCR.services.codec.image_codec import ImageCodecService, ImageCodecError


def test_encode_and_decode_roundtrip(sample_image):
    """Tests that encoding an image to Base64 and decoding it returns a valid image."""
    b64_str = ImageCodecService.encode_base64(sample_image, extension=".jpg")
    assert isinstance(b64_str, str)
    assert b64_str.startswith("data:image/jpeg;base64,")

    decoded = ImageCodecService.decode_base64(b64_str)
    assert isinstance(decoded, np.ndarray)
    assert decoded.shape[0] == sample_image.shape[0]
    assert decoded.shape[1] == sample_image.shape[1]
    assert decoded.shape[2] == 3


def test_decode_raw_base64_without_prefix(sample_image):
    """Tests decoding raw base64 string without data URI prefix."""
    b64_str = ImageCodecService.encode_base64(sample_image, extension=".png")
    raw_b64 = b64_str.split(",", 1)[1]

    decoded = ImageCodecService.decode(raw_b64)
    assert isinstance(decoded, np.ndarray)
    assert decoded.shape[:2] == sample_image.shape[:2]


def test_decode_bytes(sample_image):
    """Tests decoding directly from raw byte buffer."""
    _, buffer = cv2.imencode(".png", sample_image)
    image_bytes = buffer.tobytes()

    decoded = ImageCodecService.decode_bytes(image_bytes)
    assert isinstance(decoded, np.ndarray)
    assert decoded.shape == sample_image.shape


def test_grayscale_normalization():
    """Tests that 2D grayscale images are normalized to 3-channel BGR."""
    gray = np.ones((100, 100), dtype=np.uint8) * 128
    normalized = ImageCodecService.validate_and_normalize(gray)
    assert normalized.shape == (100, 100, 3)


def test_rgba_normalization():
    """Tests that 4-channel RGBA images are normalized to 3-channel BGR."""
    rgba = np.ones((100, 100, 4), dtype=np.uint8) * 255
    normalized = ImageCodecService.validate_and_normalize(rgba)
    assert normalized.shape == (100, 100, 3)


def test_invalid_base64_raises_error():
    """Tests that malformed base64 raises ImageCodecError."""
    with pytest.raises(ImageCodecError):
        ImageCodecService.decode_base64("this is not a valid base64 image string!!!")


def test_empty_payload_raises_error():
    """Tests that empty input raises ImageCodecError."""
    with pytest.raises(ImageCodecError):
        ImageCodecService.decode("")

    with pytest.raises(ImageCodecError):
        ImageCodecService.decode_bytes(b"")
