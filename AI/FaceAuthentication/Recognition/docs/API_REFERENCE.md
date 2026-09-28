# 📡 REST API Reference

The Face Recognition & Authentication Service exposes a REST API via FastAPI. This document details each endpoint, input schemas, and sample requests.

---

## 🌐 Base URL & Interactive Docs
- **Base URL**: `http://localhost:8000/api/v1`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

---

## 📑 Endpoints Summary

| Endpoint | Method | Input Type | Description |
| :--- | :---: | :--- | :--- |
| [`/health`](#1-health-check) | `GET` | None | Health check & service readiness |
| [`/detect`](#2-detect-faces-base64) | `POST` | JSON (Base64) | Detect faces and keypoints |
| [`/detect/file`](#3-detect-faces-multipart) | `POST` | Multipart File | Detect faces from uploaded file |
| [`/crop`](#4-align--crop-face-base64) | `POST` | JSON (Base64) | Returns 112x112 canonical aligned face |
| [`/crop/file`](#5-align--crop-face-multipart) | `POST` | Multipart File | Returns 112x112 crop from uploaded file |
| [`/embedding`](#6-extract-512-d-embedding) | `POST` | JSON (Base64) | Extracts 512-D ArcFace embedding vector |
| [`/embedding/file`](#6-extract-512-d-embedding) | `POST` | Multipart File | Extracts 512-D embedding from uploaded file |
| [`/embedding/live`](#6b-liveness-verified-pure-embedding-whole-image) | `POST` | JSON (Base64) | Whole image -> Liveness check -> Pure 512-D embedding only |
| [`/embedding/live/file`](#6b-liveness-verified-pure-embedding-whole-image) | `POST` | Multipart File | Whole image file -> Liveness -> Pure 512-D embedding only |
| [`/liveness`](#7-anti-spoofing--liveness-base64) | `POST` | JSON (Base64) | Evaluates face anti-spoofing (print/replay) |
| [`/liveness/file`](#8-anti-spoofing--liveness-multipart) | `POST` | Multipart File | Evaluates liveness from uploaded file |
| [`/verify`](#9-11-face-verification-base64) | `POST` | JSON (Base64) | 1:1 Face verification with optional liveness check |
| [`/verify/file`](#10-11-face-verification-multipart-files) | `POST` | Multipart Form | 1:1 Verification with uploaded files & liveness |
| [`/enroll`](#11-enroll-identity) | `POST` | JSON (Base64) | Register a person in gallery with photos |
| [`/identify`](#12-1n-identification) | `POST` | JSON (Base64) | Search query face against registered gallery |

---

## 1. Health Check
`GET /api/v1/health`

### Response (200 OK)
```json
{
  "status": "healthy",
  "service": "Face Recognition API"
}
```

---

## 2. Detect Faces (Base64)
`POST /api/v1/detect`

### Request Body
```json
{
  "image_base64": "/9j/4AAQSkZJRgABAQEASABIAAD..."
}
```

### Response (200 OK)
```json
{
  "success": true,
  "face_count": 1,
  "faces": [
    {
      "bbox": {
        "origin_x": 901,
        "origin_y": 2358,
        "width": 1744,
        "height": 1744
      },
      "confidence": 0.9368,
      "keypoints": [
        {"name": "right_eye", "x": 1124.0, "y": 2768.0},
        {"name": "left_eye", "x": 1733.0, "y": 2840.0},
        {"name": "nose_tip", "x": 1080.0, "y": 3168.0},
        {"name": "mouth_center", "x": 1167.0, "y": 3560.0},
        {"name": "right_ear_tragion", "x": 1050.0, "y": 2900.0},
        {"name": "left_ear_tragion", "x": 2200.0, "y": 3050.0}
      ]
    }
  ]
}
```

---

## 3. Detect Faces (Multipart)
`POST /api/v1/detect/file`

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/detect/file" \
     -H "accept: application/json" \
     -F "file=@Data/duke/duke.jpg;type=image/jpeg"
```

---

## 4. Align & Crop Face (Base64)
`POST /api/v1/crop`

### Request Body
```json
{
  "image_base64": "..."
}
```

### Response (200 OK)
```json
{
  "success": true,
  "face_count": 1,
  "image_width": 112,
  "image_height": 112,
  "cropped_face_base64": "/9j/4AAQSkZJRg..."
}
```

---

## 5. Align & Crop Face (Multipart)
`POST /api/v1/crop/file`

```bash
curl -X POST "http://localhost:8000/api/v1/crop/file" \
     -F "file=@Data/leon/leon.jpg;type=image/jpeg"
```

---

## 6. Extract 512-D Embedding
`POST /api/v1/embedding`

### Request Body
```json
{
  "image_base64": "..."
}
```

### Response (200 OK)
```json
{
  "success": true,
  "embedding_dim": 512,
  "embedding": [
    -0.0539, -0.0653, -0.0573, -0.0164, 0.0015
  ]
}
```

---

## 6B. Liveness-Verified Pure Embedding (Whole Image)
`POST /api/v1/embedding/live` & `POST /api/v1/embedding/live/file`  
*(Route aliases: `/api/v1/live-embedding`, `/api/v1/live-embedding/file`)*

Receives an uncropped **whole image** (scene or camera frame). Executes the unified pipeline:
1. **Face Detection**: Localizes the best face bounding box and landmarks.
2. **Anti-Spoofing & Liveness Check**: Evaluates presentation attacks using full image scene context ($2.7\times$ expansion). If a 2D print or screen replay is detected, the request is immediately rejected with `400 Bad Request`.
3. **Canonical Alignment**: Performs 4-point affine transformation to canonical $112\times 112$ resolution.
4. **ArcFace Embedding**: Extracts 512-D unit L2-normalized face vector.
5. **Pure Payload Response**: Returns **only** the `embedding` array, matching DTO contracts for downstream microservices (e.g., .NET `ExtractEmbeddingResponse`).

### Request Body (JSON)
```json
{
  "image_base64": "<whole_scene_image_base64>"
}
```

### Response (200 OK - Live Face)
```json
{
  "embedding": [
    0.0470, 0.0164, -0.0009, 0.0051, -0.0278, ...
  ]
}
```

### Response (400 Bad Request - Spoof Attack Detected)
```json
{
  "detail": "Liveness check failed: Spoof attack detected (replay). Real face confidence: 0.0026 < 0.60 threshold."
}
```

### cURL Example (File Upload)
```bash
curl -X POST "http://localhost:8000/api/v1/embedding/live/file" \
     -H "accept: application/json" \
     -F "file=@Data/Anti_Spoofing/real/real_1.jpg;type=image/jpeg"
```

---

## 7. Anti-Spoofing & Liveness (Base64)
`POST /api/v1/liveness`

Evaluates whether the facial image is a real live human face or a presentation spoof attack (2D printed photo or screen replay) using MiniFASNetV2.

### Request Body
```json
{
  "image_base64": "<base64_string>"
}
```

### Response (200 OK - Real Face)
```json
{
  "success": true,
  "face_count": 1,
  "liveness": {
    "is_real": true,
    "confidence": 0.9995,
    "label": "Real",
    "attack_type": null,
    "raw_scores": [0.0001, 0.9995, 0.0004]
  },
  "details": "Face is Real (confidence: 0.9995)"
}
```

### Response (200 OK - Spoof Attack Detected)
```json
{
  "success": true,
  "face_count": 1,
  "liveness": {
    "is_real": false,
    "confidence": 0.0512,
    "label": "Spoof",
    "attack_type": "print",
    "raw_scores": [0.8923, 0.0512, 0.0565]
  },
  "details": "Face is Spoof (confidence: 0.0512)"
}
```

---

## 8. Anti-Spoofing & Liveness (Multipart)
`POST /api/v1/liveness/file`

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/liveness/file" \
     -F "file=@Data/kyle/kyle.jpg;type=image/jpeg"
```

---

## 9. 1:1 Face Verification (Base64)
`POST /api/v1/verify`

Compares two facial images. When `check_liveness` is enabled (default `true` or configured via `ENABLE_LIVENESS`), both images are verified for liveness before matching. If spoofing is detected, matching is immediately rejected.

### Request Body
```json
{
  "image1_base64": "<base64_string_1>",
  "image2_base64": "<base64_string_2>",
  "threshold": 0.40,
  "check_liveness": true
}
```

### Response (200 OK)
```json
{
  "success": true,
  "match": true,
  "similarity_score": 0.5350,
  "threshold": 0.40,
  "status": "MATCH (Same Person)",
  "liveness1": {
    "is_real": true,
    "confidence": 0.9990,
    "label": "Real",
    "attack_type": null,
    "raw_scores": [0.0, 0.999, 0.001]
  },
  "liveness2": {
    "is_real": true,
    "confidence": 1.0,
    "label": "Real",
    "attack_type": null,
    "raw_scores": [0.0, 1.0, 0.0]
  }
}
```

---

## 10. 1:1 Face Verification (Multipart Files)
`POST /api/v1/verify/file`

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/verify/file" \
     -F "file1=@Data/duke/duke.jpg" \
     -F "file2=@Data/duke/duke1.jpg" \
     -F "threshold=0.40" \
     -F "check_liveness=true"
```

---

## 11. Enroll Identity
`POST /api/v1/enroll`

Registers a person into the in-memory gallery using one or more facial photos. A centroid template average is computed across all valid images. Liveness check is automatically verified to prevent spoof enrollment.

### Request Body
```json
{
  "person_id": "duke",
  "images_base64": [
    "<base64_photo_1>",
    "<base64_photo_2>"
  ],
  "check_liveness": true
}
```

### Response (200 OK)
```json
{
  "success": true,
  "person_id": "duke",
  "status": "ENROLLED",
  "enrolled_images_count": 2,
  "total_gallery_identities": 1
}
```

---

## 12. 1:N Identification
`POST /api/v1/identify`

Searches a probe query face against all registered gallery identities.

### Request Body
```json
{
  "image_base64": "<probe_photo_base64>",
  "top_k": 3,
  "threshold": 0.40,
  "check_liveness": true
}
```

### Response (200 OK)
```json
{
  "success": true,
  "identified": true,
  "top_match": {
    "person_id": "leon",
    "similarity_score": 0.6931,
    "is_match": true
  },
  "all_candidates": [
    {"person_id": "leon", "similarity_score": 0.6931, "is_match": true},
    {"person_id": "duke", "similarity_score": 0.3105, "is_match": false},
    {"person_id": "kyle", "similarity_score": 0.1280, "is_match": false}
  ]
}
```
