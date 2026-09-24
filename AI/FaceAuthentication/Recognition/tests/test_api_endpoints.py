"""
Automated Test Suite for Face Authentication & Recognition API.
"""

import base64
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.api.app import app
from src.config import DATA_DIR


def encode_file_to_base64(filepath: Path) -> str:
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_detect_file_endpoint(client):
    img_path = DATA_DIR / "duke" / "duke.jpg"
    with open(img_path, "rb") as f:
        response = client.post("/api/v1/detect/file", files={"file": ("duke.jpg", f, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    assert data["face_count"] >= 1
    assert data["faces"][0]["confidence"] > 0.80


def test_crop_json_endpoint(client):
    img_path = DATA_DIR / "leon" / "leon.jpg"
    b64 = encode_file_to_base64(img_path)
    response = client.post("/api/v1/crop", json={"image_base64": b64})
    assert response.status_code == 200
    data = response.json()
    assert data["image_width"] == 112
    assert data["image_height"] == 112
    assert len(data["cropped_face_base64"]) > 0


def test_embedding_endpoint(client):
    img_path = DATA_DIR / "kyle" / "kyle.jpg"
    b64 = encode_file_to_base64(img_path)
    response = client.post("/api/v1/embedding", json={"image_base64": b64})
    assert response.status_code == 200
    data = response.json()
    assert data["embedding_dim"] == 512
    assert len(data["embedding"]) == 512


def test_verification_match_and_mismatch(client):
    duke = encode_file_to_base64(DATA_DIR / "duke" / "duke.jpg")
    duke1 = encode_file_to_base64(DATA_DIR / "duke" / "duke1.jpg")
    kyle = encode_file_to_base64(DATA_DIR / "kyle" / "kyle.jpg")

    # Match test
    match_resp = client.post(
        "/api/v1/verify",
        json={"image1_base64": duke, "image2_base64": duke1, "threshold": 0.40},
    )
    assert match_resp.status_code == 200
    assert match_resp.json()["match"] is True

    # Mismatch test
    mismatch_resp = client.post(
        "/api/v1/verify",
        json={"image1_base64": duke, "image2_base64": kyle, "threshold": 0.40},
    )
    assert mismatch_resp.status_code == 200
    assert mismatch_resp.json()["match"] is False


def test_enrollment_and_identification(client):
    for person in ["duke", "kyle", "leon"]:
        photos = [encode_file_to_base64(p) for p in list((DATA_DIR / person).glob("*.jpg"))[:2]]
        res = client.post("/api/v1/enroll", json={"person_id": person, "images_base64": photos})
        assert res.status_code == 200
        assert res.json()["status"] == "ENROLLED"

    probe = encode_file_to_base64(DATA_DIR / "leon" / "leon3.jpg")
    id_resp = client.post("/api/v1/identify", json={"image_base64": probe, "top_k": 3, "threshold": 0.40})
    assert id_resp.status_code == 200
    data = id_resp.json()
    assert data["identified"] is True
    assert data["top_match"]["person_id"] == "leon"
