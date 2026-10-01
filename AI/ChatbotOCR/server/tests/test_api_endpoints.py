"""Integration tests for FastAPI server endpoints."""

import io
import cv2
from OCR.services.codec.image_codec import ImageCodecService


def test_health_endpoint(test_client):
    """Tests the /health endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "backend" in data


def test_rag_status_endpoint(test_client):
    """Tests the /api/v1/rag/status endpoint."""
    response = test_client.get("/api/v1/rag/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ready", "initialized")
    assert "indexed_chunks" in data


def test_ocr_info_endpoint(test_client):
    """Tests the /api/v1/ocr/info endpoint."""
    response = test_client.get("/api/v1/ocr/info")
    assert response.status_code == 200
    data = response.json()
    assert "active_backend" in data
    assert "available_backends" in data
    assert "supported_languages" in data


def test_ocr_predict_base64_endpoint(test_client, sample_image):
    """Tests POST /api/v1/ocr/predict with base64 image."""
    b64_str = ImageCodecService.encode_base64(sample_image)

    payload = {
        "image_base64": b64_str,
        "lang": "en",
        "det": True,
        "rec": True,
        "cls": True,
        "min_confidence": 0.3,
        "return_annotated_image": True,
        "sort_reading_order": True,
    }

    response = test_client.post("/api/v1/ocr/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "full_text" in data
    assert isinstance(data["lines"], list)
    assert "metadata" in data
    assert data["metadata"]["processing_time_ms"] > 0


def test_ocr_upload_multipart_endpoint(test_client, sample_image):
    """Tests POST /api/v1/ocr/upload with multipart file."""
    _, buffer = cv2.imencode(".png", sample_image)
    files = {
        "file": ("test_doc.png", io.BytesIO(buffer.tobytes()), "image/png")
    }

    response = test_client.post("/api/v1/ocr/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["lines"], list)


def test_ocr_predict_invalid_base64(test_client):
    """Tests POST /api/v1/ocr/predict with invalid base64 returns 400."""
    payload = {
        "image_base64": "invalid_base64_string_xyz!!!",
    }
    response = test_client.post("/api/v1/ocr/predict", json=payload)
    assert response.status_code == 400


def test_ocr_predict_missing_payload(test_client):
    """Tests POST /api/v1/ocr/predict with neither image_base64 nor image_url returns 422."""
    payload = {
        "lang": "en"
    }
    response = test_client.post("/api/v1/ocr/predict", json=payload)
    assert response.status_code == 422
