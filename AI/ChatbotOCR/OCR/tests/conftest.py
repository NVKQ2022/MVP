"""Pytest fixtures for OCR domain tests."""

import pytest
import numpy as np
import cv2

from OCR.services.ocr.mock_backend import MockOCRBackend
from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService


@pytest.fixture
def mock_orchestrator():
    """Provides an OCROrchestratorService instance backed by MockOCRBackend."""
    mock_backend = MockOCRBackend(
        default_text="Invoice #1024\nSubtotal: $450.00\nTax: $45.00\nTotal: $495.00"
    )
    return OCROrchestratorService(ocr_backend=mock_backend)


@pytest.fixture
def sample_image():
    """Generates a simple 3-channel test image with drawn text."""
    img = np.ones((300, 500, 3), dtype=np.uint8) * 255
    cv2.putText(img, "TEST OCR DOCUMENT", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "Second Line Info", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    return img
