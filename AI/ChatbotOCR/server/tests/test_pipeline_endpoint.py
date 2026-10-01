"""Integration tests for the End-to-End Pipeline Routes."""

import base64
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from server.app import create_app

client = TestClient(create_app())


def test_pipeline_diagnose_multipart_endpoint():
    """Test POST /api/v1/pipeline/diagnose with actual sample screenshot."""
    img_path = Path("data/sample_screenshots/kb-auth-001__01__clean_light.png")
    assert img_path.exists(), f"Sample image not found: {img_path}"

    with open(img_path, "rb") as f:
        response = client.post(
            "/api/v1/pipeline/diagnose",
            files={"file": ("screenshot.png", f, "image/png")},
            data={"pipeline": "naive", "top_k": 2},
        )

    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "ocr_text" in data
    assert "sources" in data
    assert len(data["sources"]) > 0

    # Verify recognized error text from image
    assert "401" in data["ocr_text"]
    assert "KB-AUTH-001" in str(data["sources"])


def test_pipeline_diagnose_json_endpoint():
    """Test POST /api/v1/pipeline/diagnose-json with Base64 image payload."""
    img_path = Path("data/sample_screenshots/kb-auth-001__01__clean_light.png")
    assert img_path.exists()

    b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")

    payload = {
        "image_base64": f"data:image/png;base64,{b64}",
        "message": "User cannot sign in",
        "pipeline": "naive",
        "top_k": 2,
    }

    response = client.post("/api/v1/pipeline/diagnose-json", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert data["pipeline_used"] == "naive"
    assert len(data["sources"]) > 0
