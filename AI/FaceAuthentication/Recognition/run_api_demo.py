"""
Demonstration Script: Simulates/Fakes real API requests to the Face Recognition Service
using modular dataset splits: Detection/, Recognition/, Anti_Spoofing/.
"""

import base64
from pathlib import Path
from fastapi.testclient import TestClient

from Data.download_datasets import ensure_datasets
from src.api.app import app
from src.config import (
    ANTISPOOFING_DATA_DIR,
    DATA_DIR,
    DETECTION_DATA_DIR,
    FACE_DIR,
    RECOGNITION_DATA_DIR,
)


def encode_file_to_base64(filepath: Path) -> str:
    """Reads a local image file and converts to base64 string."""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def run_demo():
    print("=" * 80)
    print("   FACE RECOGNITION & AUTHENTICATION API CLIENT SIMULATION / DEMO")
    print("=" * 80)

    # Ensure dataset splits and sample images exist
    ensure_datasets()

    # Use FastAPI TestClient for in-process request simulation without needing external server
    with TestClient(app) as client:
        # ----------------------------------------------------------------------
        # 0. Health Check
        # ----------------------------------------------------------------------
        print("\n[API Call 0] GET /api/v1/health")
        resp = client.get("/api/v1/health")
        print(f"Response ({resp.status_code}): {resp.json()}")

        # ----------------------------------------------------------------------
        # 1. Detection Request (Multipart File Upload with Multi-Face sample)
        # ----------------------------------------------------------------------
        det_img_path = DETECTION_DATA_DIR / "multi_face" / "multi_face_1.jpg"
        print(f"\n[API Call 1] POST /api/v1/detect/file (Multipart Upload: {det_img_path.name})")
        with open(det_img_path, "rb") as f:
            resp = client.post("/api/v1/detect/file", files={"file": (det_img_path.name, f, "image/jpeg")})
        
        print(f"Status Code: {resp.status_code}")
        det_data = resp.json()
        print(f"Faces Detected: {det_data['face_count']}")
        for idx, face in enumerate(det_data["faces"]):
            print(f"  Face #{idx + 1}: Confidence={face['confidence']:.4f}, BBox={face['bbox']}")

        # ----------------------------------------------------------------------
        # 2. Crop & Alignment Request (Base64 JSON Payload)
        # ----------------------------------------------------------------------
        leon_img_path = RECOGNITION_DATA_DIR / "leon" / "leon.jpg"
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
        kyle_img_path = RECOGNITION_DATA_DIR / "kyle" / "kyle.jpg"
        print(f"\n[API Call 3] POST /api/v1/embedding (Extract 512-D ArcFace Embedding)")
        kyle_b64 = encode_file_to_base64(kyle_img_path)
        resp = client.post("/api/v1/embedding", json={"image_base64": kyle_b64})
        
        print(f"Status Code: {resp.status_code}")
        emb_data = resp.json()
        print(f"Embedding Vector Dim: {emb_data['embedding_dim']}")
        print(f"First 5 Vector Values: {[round(v, 4) for v in emb_data['embedding'][:5]]}...")

        # ----------------------------------------------------------------------
        # 3B. Whole Image -> Liveness Verification -> Pure Embedding Only
        # ----------------------------------------------------------------------
        print(f"\n[API Call 3B] POST /api/v1/embedding/live (Whole Image -> Liveness -> Pure Embedding)")
        resp_live_emb = client.post("/api/v1/embedding/live", json={"image_base64": leon_b64})
        print(f"Status Code (Live Genuine): {resp_live_emb.status_code}")
        live_emb_data = resp_live_emb.json()
        print(f"Response Keys: {list(live_emb_data.keys())} (Strictly 'embedding' only)")
        print(f"Vector Length: {len(live_emb_data['embedding'])}")
        print(f"First 5 Vector Values: {[round(v, 4) for v in live_emb_data['embedding'][:5]]}...")

        print(f"\n[API Call 3C] POST /api/v1/embedding/live (Spoof Attack Defense Test)")
        spoof_demo_path = ANTISPOOFING_DATA_DIR / "spoof" / "spoof_replay_1.jpg"
        spoof_demo_b64 = encode_file_to_base64(spoof_demo_path)
        resp_spoof_emb = client.post("/api/v1/embedding/live", json={"image_base64": spoof_demo_b64})
        print(f"Status Code (Spoof Detected): {resp_spoof_emb.status_code}")
        print(f"Error Detail: {resp_spoof_emb.json()['detail']}")

        # ----------------------------------------------------------------------
        # 4. Anti-Spoofing & Liveness Checks (Real Face vs Spoof Attack)
        # ----------------------------------------------------------------------
        real_img_path = ANTISPOOFING_DATA_DIR / "real" / "real_1.jpg"
        print(f"\n[API Call 4A] POST /api/v1/liveness (Live Human Face: {real_img_path.name})")
        resp_real = client.post("/api/v1/liveness", json={"image_base64": encode_file_to_base64(real_img_path)})
        print(f"Status Code: {resp_real.status_code}")
        liv_real = resp_real.json()["liveness"]
        print(f"  Is Real: {liv_real['is_real']} ({liv_real['label']}) | Confidence: {liv_real['confidence']:.4f}")

        spoof_img_path = ANTISPOOFING_DATA_DIR / "spoof" / "spoof_replay_1.jpg"
        print(f"\n[API Call 4B] POST /api/v1/liveness (Screen Replay Spoof Attack: {spoof_img_path.name})")
        resp_spoof = client.post("/api/v1/liveness", json={"image_base64": encode_file_to_base64(spoof_img_path)})
        print(f"Status Code: {resp_spoof.status_code}")
        liv_spoof = resp_spoof.json()["liveness"]
        print(f"  Is Real: {liv_spoof['is_real']} ({liv_spoof['label']}) | Attack: {liv_spoof['attack_type']} | Confidence: {liv_spoof['confidence']:.4f}")

        # ----------------------------------------------------------------------
        # 5. 1:1 Verification (Matching vs Mismatching pairs with Liveness)
        # ----------------------------------------------------------------------
        duke_path = RECOGNITION_DATA_DIR / "duke" / "duke.jpg"
        duke1_path = RECOGNITION_DATA_DIR / "duke" / "duke1.jpg"
        print("\n[API Call 5A] POST /api/v1/verify (Matching Pair: Duke vs Duke1)")
        resp = client.post(
            "/api/v1/verify",
            json={
                "image1_base64": encode_file_to_base64(duke_path),
                "image2_base64": encode_file_to_base64(duke1_path),
                "threshold": 0.40,
                "check_liveness": True,
            },
        )
        print(f"Status Code: {resp.status_code}")
        print(f"Result: {resp.json()}")

        print("\n[API Call 5B] POST /api/v1/verify (Mismatching Pair: Duke vs Kyle)")
        resp = client.post(
            "/api/v1/verify",
            json={
                "image1_base64": encode_file_to_base64(duke_path),
                "image2_base64": encode_file_to_base64(kyle_img_path),
                "threshold": 0.40,
                "check_liveness": True,
            },
        )
        print(f"Status Code: {resp.status_code}")
        print(f"Result: {resp.json()}")

        # ----------------------------------------------------------------------
        # 6. 1:N Enrollment & Identification
        # ----------------------------------------------------------------------
        print("\n[API Call 6A] POST /api/v1/enroll (Enrolling Duke, Kyle, Leon into Gallery)")
        for person in ["duke", "kyle", "leon"]:
            photos = list((RECOGNITION_DATA_DIR / person).glob("*.jpg"))[:2]
            b64_photos = [encode_file_to_base64(p) for p in photos]
            resp = client.post(
                "/api/v1/enroll",
                json={"person_id": person, "images_base64": b64_photos},
            )
            print(f"  Enrolled '{person}': {resp.json()['status']} with {resp.json()['enrolled_images_count']} photos.")

        # Query with unseen probe image (leon3.jpg)
        probe_path = RECOGNITION_DATA_DIR / "leon" / "leon3.jpg"
        print(f"\n[API Call 6B] POST /api/v1/identify (Probe Query with {probe_path.name})")
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
