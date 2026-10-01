"""Pytest fixtures for server integration tests."""

import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient

from server.app import app


@pytest.fixture(scope="session")
def test_client():
    """Provides a TestClient connected to the FastAPI application."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_image():
    """Generates a simple 3-channel test image with drawn text."""
    img = np.ones((300, 500, 3), dtype=np.uint8) * 255
    cv2.putText(img, "TEST OCR DOCUMENT", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "Second Line Info", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    return img
