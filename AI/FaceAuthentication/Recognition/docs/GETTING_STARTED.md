# 🚀 Getting Started Guide

A quick, step-by-step guide to setting up and running the Face Authentication & Recognition Project.

---

## 📋 Prerequisites

- **OS**: Linux / macOS / Windows (WSL recommended for Linux libraries)
- **Python**: 3.10, 3.11, or 3.12
- **Virtual Environment**: `venv` or `conda`

---

## 🛠️ Step 1: Clone & Install Dependencies

1. Activate your Python virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧠 Step 2: Download Model Weights

Ensure the pretrained models (BlazeFace and ArcFace) are downloaded into the `models/` directory:

```bash
python models/download_models.py
```

This verifies and downloads:
- `models/blaze_face_short_range.tflite` (MediaPipe BlazeFace face detector, ~225 KB)
- `models/w600k_mbf.onnx` (ArcFace MobileFaceNet embedding model, ~13 MB)

---

## 🎭 Step 3: Run the API Demo Simulation

Test all system capabilities (Detection, Cropping, Embedding, Verification, and Identification) using local photos from `Data/`:

```bash
python main.py --demo
# or
python run_api_demo.py
```

---

## 🌐 Step 4: Start the Live Web API Server

Start the FastAPI HTTP server:

```bash
python main.py --serve --host 0.0.0.0 --port 8000
```

- **Interactive Swagger UI**: Open your browser at [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: Open [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 💻 Step 5: Command-Line Operations (CLI)

### 1. 1:1 Verification Between Two Photos
Compare any two photos (e.g. check if Duke is Duke):
```bash
python main.py --action verify --img1 Data/duke/duke.jpg --img2 Data/duke/duke1.jpg
```
Output:
```text
Similarity Score: 0.5353 (Threshold: 0.40)
Decision: MATCH (Same Person)
```

### 2. Process Entire Dataset & Compute Similarity Matrix
Detects all faces in `Data/`, saves aligned crops to `Face/`, and prints evaluation metrics:
```bash
python main.py --action all
```

---

## 🧪 Step 6: Run Automated Tests

Run the full automated test suite to ensure all endpoints and services are working:

```bash
pytest tests/ -v
```
