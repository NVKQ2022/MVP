# 📚 PaddleOCR API Reference

Interactive Swagger UI documentation is available at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

---

## 🌐 Endpoints Overview

| Method | Endpoint | Description | Request Body / Params |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health status & backend probe | None |
| `GET` | `/api/v1/ocr/info` | Query registered backends & supported languages | None |
| `POST` | `/api/v1/ocr/predict` | Run OCR on Base64 or Image URL | `application/json` (`OCRPredictRequest`) |
| `POST` | `/api/v1/ocr/upload` | Run OCR on uploaded image file | `multipart/form-data` (`file`) |

---

## 1. `GET /health`

### Response:
```json
{
  "status": "healthy",
  "app_name": "PaddleOCR API Service",
  "version": "1.0.0",
  "backend": "PaddleOCR",
  "device": "CPU"
}
```

---

## 2. `GET /api/v1/ocr/info`

### Response:
```json
{
  "active_backend": "PaddleOCR",
  "available_backends": [
    "mock",
    "paddle",
    "paddleocr"
  ],
  "supported_languages": [
    "en",
    "ch",
    "korean",
    "japan",
    "chinese_cht",
    "ta",
    "te",
    "ka",
    "latin",
    "arabic",
    "cyrillic",
    "devanagari",
    "french",
    "german"
  ],
  "use_gpu": false
}
```

---

## 3. `POST /api/v1/ocr/predict`

Accepts JSON payload with Base64 or URL.

### Request Body:
```json
{
  "image_base64": "data:image/jpeg;base64,...",
  "image_url": null,
  "lang": "en",
  "det": true,
  "rec": true,
  "cls": true,
  "min_confidence": 0.5,
  "return_annotated_image": true,
  "sort_reading_order": true
}
```

### Response Body:
```json
{
  "success": true,
  "message": "Successfully extracted 4 text line(s).",
  "total_lines": 4,
  "full_text": "ACME SUPERMARKET CORP\n123 AI Boulevard, Tech City\nTOTAL AMOUNT: $308.97\nTHANK YOU FOR YOUR PURCHASE!",
  "lines": [
    {
      "text": "ACME SUPERMARKET CORP",
      "confidence": 0.985,
      "polygon": [[160, 60], [480, 60], [480, 95], [160, 95]],
      "box_2d": [160, 60, 480, 95]
    }
  ],
  "annotated_image_base64": "data:image/jpeg;base64,...",
  "metadata": {
    "backend": "PaddleOCR",
    "language": "en",
    "image_width": 700,
    "image_height": 450,
    "processing_time_ms": 125.4,
    "inference_time_ms": 118.2,
    "device": "CPU"
  }
}
```

---

## 4. `POST /api/v1/ocr/upload`

Upload a multipart image file directly.

### Query Parameters:
- `lang` (optional, string): e.g. `"en"`
- `min_confidence` (optional, float): e.g. `0.5`
- `return_annotated_image` (optional, bool): e.g. `false`
- `sort_reading_order` (optional, bool): e.g. `true`

### cURL Example:
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/upload?lang=en&min_confidence=0.5" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@receipt.jpg;type=image/jpeg"
```
