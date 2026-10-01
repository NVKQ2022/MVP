# 🚀 Getting Started

Quick start guide for installing, running, and testing the PaddleOCR API service.

---

## 📦 1. Installation

```bash
# Clone or navigate to OCR directory
cd /home/quan/projects/maivenpoint/AI/OCR

# Install dependencies
pip install -r requirements.txt
```

---

## 🏃 2. Starting the API Server

```bash
# Start server using main.py
python3 main.py --host 0.0.0.0 --port 8000

# Or using Uvicorn directly
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🎭 3. Running In-Process Demo Simulation

Run the automated in-process demonstration script:
```bash
python3 run_api_demo.py
```
This will:
1. Verify the `/health` endpoint.
2. Query backend info at `/api/v1/ocr/info`.
3. Generate a sample synthetic receipt image.
4. Send Base64 OCR prediction request and print extracted text.
5. Save the visual annotated output with drawn bounding boxes to `demo_output/annotated_result.jpg`.
6. Test multipart upload at `/api/v1/ocr/upload`.

---

## 📄 4. Direct CLI Mode

Run OCR directly on an image from the terminal without starting a server:
```bash
python3 main.py --file path/to/image.jpg --lang en --save-annotated output_annotated.jpg
```

---

## 🧪 5. Running Automated Tests

```bash
pytest
```
