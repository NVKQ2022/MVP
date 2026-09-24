# 📡 REST API Reference

The Face Recognition Service exposes a REST API via FastAPI. This document details each endpoint, input schemas, and sample requests.

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
| [`/embedding`](#6-extract-embedding) | `POST` | JSON (Base64) | Extracts 512-D ArcFace embedding vector |
| [`/verify`](#7-11-face-verification-base64) | `POST` | JSON (Base64) | 1:1 Face verification between two images |
| [`/verify/file`](#8-11-face-verification-multipart) | `POST` | Multipart Form | 1:1 Verification with uploaded files |
| [`/enroll`](#9-enroll-identity) | `POST` | JSON (Base64) | Register a person in gallery with photos |
| [`/identify`](#10-1n-identification) | `POST` | JSON (Base64) | Search query face against registered gallery |

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

## 5. Extract 512-D Embedding
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
    -0.0539, -0.0653, -0.0573, -0.0164, 0.0015, ...
  ]
}
```

---

## 6. 1:1 Face Verification (Base64)
`POST /api/v1/verify`

### Request Body
```json
{
  "image1_base64": "<base64_string_1>",
  "image2_base64": "<base64_string_2>",
  "threshold": 0.40
}
```

### Response (200 OK)
```json
{
  "success": true,
  "match": true,
  "similarity_score": 0.5353,
  "threshold": 0.40,
  "status": "MATCH (Same Person)"
}
```

---

## 7. 1:1 Face Verification (Multipart Files)
`POST /api/v1/verify/file`

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/verify/file" \
     -F "file1=@Data/duke/duke.jpg" \
     -F "file2=@Data/duke/duke1.jpg" \
     -F "threshold=0.40"
```

---

## 8. Enroll Identity
`POST /api/v1/enroll`

### Request Body
```json
{
  "person_id": "duke",
  "images_base64": [
    "<base64_photo_1>",
    "<base64_photo_2>"
  ]
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

## 9. 1:N Identification
`POST /api/v1/identify`

### Request Body
```json
{
  "image_base64": "<probe_photo_base64>",
  "top_k": 3,
  "threshold": 0.40
}
```

### Response (200 OK)
```json
{
  "success": true,
  "identified": true,
  "top_match": {
    "person_id": "leon",
    "similarity_score": 0.6917,
    "is_match": true
  },
  "all_candidates": [
    {"person_id": "leon", "similarity_score": 0.6917, "is_match": true},
    {"person_id": "duke", "similarity_score": 0.3099, "is_match": false},
    {"person_id": "kyle", "similarity_score": 0.1273, "is_match": false}
  ]
}
```
