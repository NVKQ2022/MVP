# 🔍 PaddleOCR Python REST API Server

Production-ready, highly extensible Optical Character Recognition (OCR) API server powered by **PaddleOCR** and **FastAPI**, designed strictly adhering to the architectural patterns in [`DESIGNPATTERN.md`](./DESIGNPATTERN.md).

---

## 🌟 Highlights

- **Clean Architecture & SOLID Design**: Fully decoupled controller, orchestrator, strategy backends, codec adapters, and Pydantic DTO layers.
- **PaddleOCR Engine**: High-accuracy multi-language detection, angle classification, and recognition.
- **Swappable Strategy & Factory**: Abstract `BaseOCRBackend` contract allowing seamless addition of new backends (Mock, Paddle, Tesseract, etc.).
- **Universal Codec**: Ingests Base64 (with/without Data URI), image URLs, multipart file uploads, or raw byte buffers.
- **Natural Reading Order Sorter**: Automatically groups and sorts text lines top-to-bottom and left-to-right.
- **Visual Annotations**: Optional Base64 JPEG preview with bounding polygons and confidence tags rendered.
- **Multi-Modal Execution**: Run as REST API server, in-process test simulation, or direct CLI command tool.

---

## 📁 Project Structure

```text
OCR/
├── DESIGNPATTERN.md              # 📐 Architecture blueprint & guidelines
├── requirements.txt              # 📦 Pinned dependencies
├── pytest.ini                    # 🧪 Pytest configuration
├── main.py                       # 🚀 Server entrypoint & CLI OCR runner
├── run_api_demo.py               # 🎭 In-process simulation & verification script
├── src/
│   ├── __init__.py
│   ├── config.py                 # ⚙️ Centralized environment configuration
│   ├── schemas/                  # 📋 Pydantic DTO Schemas
│   │   ├── __init__.py
│   │   ├── request_schemas.py    # Input payloads (Base64, URL, config)
│   │   └── response_schemas.py   # Output responses (lines, polygons, metadata)
│   ├── services/                 # 🏛️ Domain Services Layer
│   │   ├── __init__.py
│   │   ├── base/                 # Abstract Base Classes (Contracts)
│   │   │   ├── __init__.py
│   │   │   └── base_ocr.py       # BaseOCRBackend(ABC)
│   │   ├── ocr/                  # Concrete OCR Strategies & Factory
│   │   │   ├── __init__.py
│   │   │   ├── paddle_backend.py # PaddleOCRBackend
│   │   │   ├── mock_backend.py   # MockOCRBackend
│   │   │   └── factory.py        # OCRFactory (Registry pattern)
│   │   ├── codec/                # Universal Input/Output Adapters
│   │   │   ├── __init__.py
│   │   │   └── image_codec.py    # ImageCodecService
│   │   ├── visualizer/           # Visual Annotator Service
│   │   │   ├── __init__.py
│   │   │   └── annotator.py      # OCRVisualizerService
│   │   └── orchestrator/         # Domain Orchestrator Facade
│   │       ├── __init__.py
│   │       └── ocr_orchestrator.py # High-level business pipeline
│   ├── api/                      # 🌐 FastAPI REST Layer
│   │   ├── __init__.py
│   │   ├── app.py                # App factory, CORS, Lifespan warm-up
│   │   ├── routes.py             # Thin controller endpoints (<= 5-10 lines)
│   │   └── dependencies.py       # Dependency injection providers
│   └── utils/                    # 🛠️ Utility Modules
│       ├── __init__.py
│       ├── logger.py             # Structured logging
│       ├── timing.py             # High-precision timer context
│       └── ordering.py           # Natural reading order sorter
├── tests/                        # 🧪 Automated Test Suite (18 tests)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_codec.py
│   ├── test_ordering.py
│   ├── test_orchestrator.py
│   └── test_api_endpoints.py
└── docs/                         # 📚 Detailed Documentation
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    └── GETTING_STARTED.md
```

---

## 🚀 Quick Start

### 1. Run the Verification Demo
```bash
python3 run_api_demo.py
```

### 2. Start the API Server
```bash
python3 main.py --host 0.0.0.0 --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser for the interactive OpenAPI documentation.

### 3. Run Direct CLI OCR
```bash
python3 main.py --file demo_output/sample_invoice.jpg --save-annotated demo_output/result.jpg
```

### 4. Run Pytest Suite
```bash
pytest
```

---

## 📖 Documentation Links

- [🧠 AI & Computer Vision Theory Guide](docs/THEORY_AND_COMPUTER_VISION.md)
- [📐 Architecture & Design Patterns](docs/ARCHITECTURE.md)
- [📚 API Reference & Schema Examples](docs/API_REFERENCE.md)
- [🚀 Getting Started Guide](docs/GETTING_STARTED.md)
- [📐 Design Pattern Specification](DESIGNPATTERN.md)
