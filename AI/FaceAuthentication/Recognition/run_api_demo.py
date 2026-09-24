"""
Demonstration Script: Simulates/Fakes real API requests to the Face Recognition Service
using local images from the Data/ directory.
"""

import base64
from pathlib import Path
from fastapi.testclient import TestClient

from src.api.app import app
from src.config import DATA_DIR, FACE_DIR


def encode_file_to_base64(filepath: Path) -> str:
    """Reads a local image file and converts to base64 string."""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def run_demo():
    print("=" * 80)
    print("   FACE RECOGNITION API CLIENT SIMULATION / DEMO")
    print("=" * 80)

    # Use FastAPI TestClient for in-process request simulation without needing external server
    with TestClient(app) as client:
        # ----------------------------------------------------------------------
        # 0. Health Check
        # ----------------------------------------------------------------------
        print("\n[API Call 0] GET /api/v1/health")
        resp = client.get("/api/v1/health")
        print(f"Response ({resp.status_code}): {resp.json()}")

        # ----------------------------------------------------------------------
        # 1. Detection Request (Multipart File Upload)
        # ----------------------------------------------------------------------
        duke_img_path = DATA_DIR / "duke" / "duke.jpg"
        print(f"\n[API Call 1] POST /api/v1/detect/file (Multipart Upload: {duke_img_path.name})")
        with open(duke_img_path, "rb") as f:
            resp = client.post("/api/v1/detect/file", files={"file": ("duke.jpg", f, "image/jpeg")})
        
        print(f"Status Code: {resp.status_code}")
        det_data = resp.json()
        print(f"Faces Detected: {det_data['face_count']}")
        if det_data["faces"]:
            face = det_data["faces"][0]
            print(f"  Confidence: {face['confidence']:.4f}")
            print(f"  Bounding Box: {face['bbox']}")
            print(f"  Landmarks Count: {len(face['keypoints'])} ({[kp['name'] for kp in face['keypoints']]})")

        # ----------------------------------------------------------------------
        # 2. Crop & Alignment Request (Base64 JSON Payload)
        # ----------------------------------------------------------------------
        leon_img_path = DATA_DIR / "leon" / "leon.jpg"
        print(f"\n[API Call 2] POST /api/v1/crop (Base64 JSON: {leon_img_path.name})")
        leon_b64 = encode_file_to_base64(leon_img_path)
        resp = client.post("/api/v1/crop", json={"image_base64": leon_b64})
        
        print(f"Status Code: {resp.status_code}")
        crop_data = resp.json()
        print(f"Cropped Output Resolution: {crop_data['image_width']}x{crop_data['image_height']}")
        print(f"Base64 Crop String Length: {len(crop_data['cropped_face_base64'])} chars")

        # Save cropped face to Face/ directory to demonstrate crop output
        out_face_dir = FACE_DIR / "api_demo_output"
        out_face_dir.mkdir(parents=True, exist_ok=True)
        crop_bytes = base64.b64decode(crop_data["cropped_face_base64"])
        out_crop_path = out_face_dir / "leon_aligned_crop_112x112.jpg"
        with open(out_crop_path, "wb") as f:
            f.write(crop_bytes)
        print(f"  Saved demo crop to: {out_crop_path}")

        # ----------------------------------------------------------------------
        # 3. Embedding Request (Base64 JSON Payload)
        # ----------------------------------------------------------------------
        kyle_img_path = DATA_DIR / "kyle" / "kyle.jpg"
        print(f"\n[API Call 3] POST /api/v1/embedding (Extract 512-D ArcFace Embedding)")
        kyle_b64 = encode_file_to_base64(kyle_img_path)
        resp = client.post("/api/v1/embedding", json={"image_base64": kyle_b64})
        
        print(f"Status Code: {resp.status_code}")
        emb_data = resp.json()
        print(f"Embedding Vector Dim: {emb_data['embedding_dim']}")
        print(f"First 5 Vector Values: {[round(v, 4) for v in emb_data['embedding'][:5]]}...")

        # ----------------------------------------------------------------------
        # 4. 1:1 Verification (Matching vs Mismatching pairs)
        # ----------------------------------------------------------------------
        duke1_path = DATA_DIR / "duke" / "duke1.jpg"
        print("\n[API Call 4A] POST /api/v1/verify (Matching Pair: Duke vs Duke1)")
        resp = client.post(
            "/api/v1/verify",
            json={
                "image1_base64": encode_file_to_base64(duke_img_path),
                "image2_base64": encode_file_to_base64(duke1_path),
                "threshold": 0.40,
            },
        )
        print(f"Status Code: {resp.status_code}")
        print(f"Result: {resp.json()}")

        print("\n[API Call 4B] POST /api/v1/verify (Mismatching Pair: Duke vs Kyle)")
        resp = client.post(
            "/api/v1/verify",
            json={
                "image1_base64": encode_file_to_base64(duke_img_path),
                "image2_base64": encode_file_to_base64(kyle_img_path),
                "threshold": 0.40,
            },
        )
        print(f"Status Code: {resp.status_code}")
        print(f"Result: {resp.json()}")

        # ----------------------------------------------------------------------
        # 5. 1:N Enrollment & Identification
        # ----------------------------------------------------------------------
        print("\n[API Call 5A] POST /api/v1/enroll (Enrolling Duke, Kyle, Leon into Gallery)")
        for person in ["duke", "kyle", "leon"]:
            photos = list((DATA_DIR / person).glob("*.jpg"))[:2]  # Enroll with first 2 photos
            b64_photos = [encode_file_to_base64(p) for p in photos]
            resp = client.post(
                "/api/v1/enroll",
                json={"person_id": person, "images_base64": b64_photos},
            )
            print(f"  Enrolled '{person}': {resp.json()['status']} with {resp.json()['enrolled_images_count']} photos.")

        # Query with unseen probe image (leon3.jpg)
        probe_path = DATA_DIR / "leon" / "leon3.jpg"
        print(f"\n[API Call 5B] POST /api/v1/identify (Probe Query with {probe_path.name})")
        resp = client.post(
            "/api/v1/identify",
            json={"image_base64": encode_file_to_base64(probe_path), "top_k": 3, "threshold": 0.40},
        )
        print(f"Status Code: {resp.status_code}")
        id_data = resp.json()
        print(f"Identified: {id_data['identified']}")
        print(f"Top Match: Person '{id_data['top_match']['person_id']}' with Similarity = {id_data['top_match']['similarity_score']:.4f}")
        print("All Candidates Ranked:")
        for cand in id_data["all_candidates"]:
            print(f"  - {cand['person_id']:<10}: Score = {cand['similarity_score']:.4f} (Match: {cand['is_match']})")

    print("\n" + "=" * 80)
    print("   ALL API SIMULATION REQUESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
