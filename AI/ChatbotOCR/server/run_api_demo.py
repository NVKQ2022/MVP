import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import os
import io
import json
import cv2
import numpy as np
from fastapi.testclient import TestClient

from server.app import app
from OCR.services.codec.image_codec import ImageCodecService


def create_sample_receipt_image() -> np.ndarray:
    """Generates a clean synthetic receipt image with multiple text lines."""
    img = np.ones((450, 700, 3), dtype=np.uint8) * 255

    # Draw border
    cv2.rectangle(img, (15, 15), (685, 435), (200, 200, 200), 2)

    # Add text lines
    lines = [
        ("ACME SUPERMARKET CORP", (160, 60), 0.9, 2),
        ("123 AI Boulevard, Tech City", (190, 100), 0.6, 1),
        ("--------------------------------------------------", (50, 140), 0.6, 1),
        ("ITEM                       QTY       PRICE", (60, 180), 0.6, 2),
        ("PaddleOCR Pro License       1       $199.00", (60, 220), 0.6, 1),
        ("Vision AI Acceleration Pack 2        $59.98", (60, 260), 0.6, 1),
        ("FastAPI Microservice Core   1        $49.99", (60, 300), 0.6, 1),
        ("--------------------------------------------------", (50, 340), 0.6, 1),
        ("TOTAL AMOUNT:                       $308.97", (60, 380), 0.7, 2),
        ("THANK YOU FOR YOUR PURCHASE!", (170, 415), 0.6, 1),
    ]

    for text, (x, y), scale, thickness in lines:
        cv2.putText(
            img,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            (20, 20, 20),
            thickness,
            cv2.LINE_AA,
        )

    return img


def main():
    print("=" * 70)
    print("🚀 CHATBOTOCR API SERVER VERIFICATION DEMO")
    print("=" * 70)

    output_dir = "demo_output"
    os.makedirs(output_dir, exist_ok=True)

    with TestClient(app) as client:
        # 1. Health Check
        print("\n[Step 1] Checking Service Health Probe (/health)...")
        resp = client.get("/health")
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        assert resp.status_code == 200, "Health check failed!"

        # 2. RAG Status Check
        print("\n[Step 2] Checking RAG Status (/api/v1/rag/status)...")
        resp = client.get("/api/v1/rag/status")
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        assert resp.status_code == 200, "RAG status endpoint failed!"

        # 3. Get OCR Info
        print("\n[Step 3] Querying OCR Backend Info (/api/v1/ocr/info)...")
        resp = client.get("/api/v1/ocr/info")
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        assert resp.status_code == 200, "Info endpoint failed!"

        # 4. Create Sample Image
        print("\n[Step 4] Generating Synthetic Test Invoice Image...")
        sample_img = create_sample_receipt_image()
        sample_img_path = os.path.join(output_dir, "sample_invoice.jpg")
        cv2.imwrite(sample_img_path, sample_img)
        print(f"Saved sample image to '{sample_img_path}'")

        # Encode to Base64
        base64_payload = ImageCodecService.encode_base64(sample_img)

        # 5. Test Base64 Predict Endpoint
        print("\n[Step 5] Calling Base64 Predict Endpoint (/api/v1/ocr/predict)...")
        predict_payload = {
            "image_base64": base64_payload,
            "lang": "en",
            "det": True,
            "rec": True,
            "cls": True,
            "min_confidence": 0.5,
            "return_annotated_image": True,
            "sort_reading_order": True,
        }
        resp = client.post("/api/v1/ocr/predict", json=predict_payload)
        print(f"Status Code: {resp.status_code}")
        data = resp.json()
        assert resp.status_code == 200, f"Predict endpoint failed: {resp.text}"

        print(f"\n📊 Total Lines Detected: {data['total_lines']}")
        print(f"⏱️ Total Processing Time: {data['metadata']['processing_time_ms']} ms")
        print(f"⚙️ Backend Engine: {data['metadata']['backend']}")

        print("\n📝 Extracted Text Output:")
        print("-" * 50)
        print(data["full_text"])
        print("-" * 50)

        # Save annotated image
        if data.get("annotated_image_base64"):
            annotated = ImageCodecService.decode(data["annotated_image_base64"])
            annotated_path = os.path.join(output_dir, "server_annotated_result.jpg")
            cv2.imwrite(annotated_path, annotated)
            print(f"🖼️ Saved visual bounding box output to: '{annotated_path}'")

        # 6. Test Multipart File Upload Endpoint
        print("\n[Step 6] Calling Multipart Upload Endpoint (/api/v1/ocr/upload)...")
        _, img_encoded = cv2.imencode(".jpg", sample_img)
        files = {
            "file": ("invoice.jpg", io.BytesIO(img_encoded.tobytes()), "image/jpeg")
        }
        params = {
            "lang": "en",
            "min_confidence": 0.5,
            "return_annotated_image": False,
        }
        resp = client.post("/api/v1/ocr/upload", files=files, params=params)
        print(f"Status Code: {resp.status_code}")
        assert resp.status_code == 200, f"Upload endpoint failed: {resp.text}"
        upload_data = resp.json()
        print(f"Upload Result Total Lines: {upload_data['total_lines']}")
        print(f"Success: {upload_data['success']}")

    print("\n" + "=" * 70)
    print("🎉 ALL SERVER ENDPOINTS SIMULATED & VERIFIED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
