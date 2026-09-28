# Hierarchical Face Recognition & Authentication Services

A production-grade Face Detection, Anti-Spoofing (Liveness Check), and Recognition framework built with a **Hierarchical Service Class Architecture**, **Factory Design Pattern**, and **FastAPI REST Endpoints**. Models and preprocessing strategies are swappable via configuration without modifying application logic.

---

## 🏛️ Hierarchical Service Architecture

```mermaid
classDiagram
    %% Base Interfaces
    class BaseFaceDetectionService {
        <<abstract>>
        +detect(image_input) List~FaceDetectionDTO~*
        +detect_best(image_input) FaceDetectionDTO
        +model_name str*
        +close()
    }
    class BaseFacePreprocessingService {
        <<abstract>>
        +align_and_crop(image_bgr, detection) ndarray*
        +normalize_tensor(face_bgr) ndarray*
        +normalize_batch(faces_bgr) ndarray
        +target_size tuple*
    }
    class BaseAntiSpoofingService {
        <<abstract>>
        +check_liveness(image_bgr, bbox) LivenessDTO*
        +model_name str*
        +close()
    }
    class BaseFaceEmbeddingService {
        <<abstract>>
        +extract(tensor, normalize) ndarray*
        +extract_batch(batch_tensor, normalize) ndarray*
        +cosine_similarity(emb1, emb2) float
        +embedding_dim int*
        +model_name str*
        +close()
    }

    %% Concrete Detection Services
    class BlazeFaceDetectionService {
        +detect(image_input) List~FaceDetectionDTO~
        +model_name "MediaPipe BlazeFace Short-Range"
    }
    BaseFaceDetectionService <|-- BlazeFaceDetectionService

    %% Concrete Preprocessing Services
    class CanonicalLandmarkPreprocessingService {
        +align_and_crop(image_bgr, detection) ndarray
        +normalize_tensor(face_bgr) ndarray
    }
    class BBoxCropPreprocessingService {
        +align_and_crop(image_bgr, detection) ndarray
        +normalize_tensor(face_bgr) ndarray
    }
    BaseFacePreprocessingService <|-- CanonicalLandmarkPreprocessingService
    BaseFacePreprocessingService <|-- BBoxCropPreprocessingService

    %% Concrete Anti-Spoofing Services
    class MiniFASNetAntiSpoofingService {
        +check_liveness(image_bgr, bbox) LivenessDTO
        +model_name "MiniFASNetV2"
    }
    BaseAntiSpoofingService <|-- MiniFASNetAntiSpoofingService

    %% Concrete Embedding Services
    class ArcFaceEmbeddingService {
        +extract(tensor, normalize) ndarray
        +extract_batch(batch_tensor, normalize) ndarray
        +embedding_dim 512
        +model_name "ArcFace (MobileFaceNet)"
    }
    BaseFaceEmbeddingService <|-- ArcFaceEmbeddingService

    %% Orchestrator
    class FaceRecognitionService {
        -detector: BaseFaceDetectionService
        -preprocessor: BaseFacePreprocessingService
        -antispoof: BaseAntiSpoofingService
        -embedder: BaseFaceEmbeddingService
        +get_live_face_embedding(image_input) List~float~
        +check_liveness(image_input) LivenessResponse
        +verify(image1, image2, threshold) VerifyResponse
        +enroll(person_id, images) EnrollResponse
        +identify(query_image, top_k) IdentifyResponse
    }
    FaceRecognitionService o-- BaseFaceDetectionService
    FaceRecognitionService o-- BaseFacePreprocessingService
    FaceRecognitionService o-- BaseAntiSpoofingService
    FaceRecognitionService o-- BaseFaceEmbeddingService
```

---

## 📁 Directory Layout

```text
Recognition/
├── src/
│   ├── config.py                     # Central configuration & dynamic model selectors
│   ├── schemas/                      # Pydantic DTOs
│   │   ├── request_schemas.py        # Base64ImagePayload, VerifyBase64Request, EnrollRequest, IdentifyRequest
│   │   └── response_schemas.py       # PureEmbeddingResponse, DetectResponse, CropResponse, LivenessResponse, VerifyResponse, IdentifyResponse
│   ├── services/                     # Hierarchical Services Layer
│   │   ├── base/                     # Root Abstract Interfaces (ABCs)
│   │   │   ├── base_detection.py     # BaseFaceDetectionService
│   │   │   ├── base_preprocessing.py # BaseFacePreprocessingService
│   │   │   ├── base_antispoofing.py  # BaseAntiSpoofingService
│   │   │   └── base_embedding.py     # BaseFaceEmbeddingService
│   │   ├── detection/                # Detection Backends
│   │   │   ├── blazeface_service.py  # BlazeFaceDetectionService
│   │   │   └── factory.py            # DetectionServiceFactory
│   │   ├── preprocessing/            # Preprocessing Backends
│   │   │   ├── landmark_align_service.py # CanonicalLandmarkPreprocessingService (4-point affine)
│   │   │   ├── bbox_crop_service.py      # BBoxCropPreprocessingService (margin crop)
│   │   │   └── factory.py                # PreprocessingServiceFactory
│   │   ├── antispoofing/             # Anti-Spoofing & Liveness Backends
│   │   │   ├── minifasnet_service.py # MiniFASNetAntiSpoofingService (ONNX)
│   │   │   └── factory.py            # AntiSpoofingServiceFactory
│   │   ├── embedding/                # Embedding Backends
│   │   │   ├── arcface_service.py    # ArcFaceEmbeddingService (ONNX)
│   │   │   └── factory.py            # EmbeddingServiceFactory
│   │   ├── codec/                    # Universal Image Codec Adapters
│   │   │   └── image_codec.py        # Decodes Bytes/Base64/File/Array
│   │   └── orchestrator/             # High-Level Orchestrator
│   │       └── recognition_service.py # FaceRecognitionService Facade
│   ├── api/                          # REST API Layer
│   │   ├── app.py                    # FastAPI application & lifecycle
│   │   └── routes.py                 # REST API endpoints
│   └── utils/                        # Utilities
│       ├── image_io.py               # File loading, saving & visualization
│       └── metrics.py                # Evaluation & distance metrics
├── tests/                            # Automated Tests (Pytest)
│   └── test_api_endpoints.py         # End-to-end API integration tests
├── models/                           # Model weights & downloader
│   └── download_models.py            # Automated downloader for BlazeFace, ArcFace, MiniFASNet
├── Data/                             # Modular Dataset Splits (Placeholders tracked)
│   ├── Detection/                    # Single-face & multi-face detection samples
│   ├── Recognition/                  # Subject identity galleries (duke, kyle, leon)
│   ├── Anti_Spoofing/                # Live captures & presentation spoof attacks
│   └── download_datasets.py          # Automated downloader for sample dataset (~800 KB)
├── docs/                             # Comprehensive Documentation
│   ├── API_REFERENCE.md              # Complete REST API documentation
│   ├── ARCHITECTURE.md               # Architectural patterns & layer contracts
│   ├── DESIGNPATTERN.md              # Universal Python microservice blueprint
│   └── GETTING_STARTED.md            # Quickstart guide
├── main.py                           # CLI & Web Server runner
├── run_api_demo.py                   # API simulation client faking requests with local Data/
├── requirements.txt                  # Python dependencies
└── README.md                         # Documentation
```

---

## ⚙️ Dynamic Model Switching via Config

You can switch detection, anti-spoofing, preprocessing, or recognition models in [src/config.py](file:///home/quan/projects/maivenpoint/AI/FaceAuthentication/Recognition/src/config.py) or via environment variables:

```bash
# Switch strategies dynamically:
export DETECTION_BACKBONE="blazeface"       # options: blazeface
export ANTISPOOFING_BACKBONE="minifasnet"   # options: minifasnet
export ENABLE_LIVENESS="true"               # options: true, false
export LIVENESS_THRESHOLD="0.60"            # float in [0.0, 1.0]
export PREPROCESSING_TYPE="landmark_affine" # options: landmark_affine, bbox_crop
export EMBEDDING_BACKBONE="arcface"         # options: arcface

./venv/bin/python main.py --demo
```

---

## 🔌 How to Add a New Model Backend in the Future

Adding a new model (e.g. **RetinaFace**, **FAS-CDCN**, or **AdaFace**) takes only 2 simple steps:

### Step 1: Subclass the Root Base Interface
```python
# src/services/embedding/adaface_service.py
from src.services.base import BaseFaceEmbeddingService

class AdaFaceEmbeddingService(BaseFaceEmbeddingService):
    def __init__(self, model_path=None):
        # Load AdaFace weights...
        pass

    @property
    def model_name(self) -> str:
        return "AdaFace (ResNet-50)"

    @property
    def embedding_dim(self) -> int:
        return 512

    def extract(self, tensor, normalize=True):
        # Run inference...
        return embedding

    def extract_batch(self, batch_tensor, normalize=True):
        return embeddings
```

### Step 2: Register in the Factory
```python
# In src/services/embedding/factory.py
EmbeddingServiceFactory.register("adaface", AdaFaceEmbeddingService)
```
Now setting `export EMBEDDING_BACKBONE="adaface"` automatically activates AdaFace across all API endpoints and CLI commands without touching any existing business logic!

---

## 🚀 Execution Commands

### 1. Run Automated Test Suite
```bash
./venv/bin/pytest tests/
```

### 2. Run API Simulation Demo (Faking API Requests using `Data/`)
```bash
./venv/bin/python main.py --demo
# or
./venv/bin/python run_api_demo.py
```

### 3. Start Live FastAPI Web Server
```bash
./venv/bin/python main.py --serve --port 8000
```
Swagger UI docs: **`http://localhost:8000/docs`**

### 4. Fetch Sample Datasets (~800 KB)
```bash
./venv/bin/python Data/download_datasets.py
```

### 5. CLI Liveness / Anti-Spoofing Check
```bash
./venv/bin/python main.py --action liveness --img1 Data/Anti_Spoofing/real/real_1.jpg
```

### 6. CLI 1:1 Verification with Liveness
```bash
./venv/bin/python main.py --action verify --img1 Data/Recognition/duke/duke.jpg --img2 Data/Recognition/duke/duke1.jpg
```

### 7. CLI Full Dataset Evaluation Matrix
```bash
./venv/bin/python main.py --action all
```
