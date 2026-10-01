# 🤖 ChatbotOCR: Modular AI Architecture

Unified, production-ready AI service platform split into three decoupled subsystems: **OCR**, **RAG**, and **server**, built strictly adhering to Clean Architecture and SOLID design principles.

---

## 📁 Repository Structure

```text
ChatbotOCR/
├── main.py                       # 🚀 Root entrypoint (launches server or direct CLI OCR)
├── requirements.txt              # 📦 Unified dependency manifest
├── pytest.ini                    # 🧪 Pytest configuration for all test suites
├── .gitignore                    # 🙈 Git ignore specifications
├── README.md                     # 📖 This documentation file
│
├── OCR/                          # 🔍 OCR Domain Subsystem
│   ├── __init__.py               # Clean public interface exports
│   ├── config.py                 # OCR engine configuration
│   ├── cli.py                    # Direct CLI OCR command runner
│   ├── schemas/                  # Pydantic DTOs (Request/Response)
│   ├── services/                 # Business logic, factories, backends, codec
│   │   ├── base/                 # Base interfaces (BaseOCRBackend ABC)
│   │   ├── ocr/                  # PaddleOCR & Mock backends + Factory
│   │   ├── codec/                # Universal image codec adapter
│   │   ├── visualizer/           # Visual polygon & bounding box annotator
│   │   └── orchestrator/         # OCROrchestratorService facade
│   ├── utils/                    # Logger, timing, reading order sorter
│   ├── tests/                    # OCR domain unit tests
│   └── docs/                     # OCR & Computer Vision theory and documentation
│
├── RAG/                          # 🧠 RAG Domain Subsystem
│   ├── __init__.py               # RAG package initialization
│   ├── README.md                 # Documentation (to be guided by user)
│   ├── config.py                 # RAG configuration settings
│   └── services/                 # Placeholder for upcoming RAG services
│
└── server/                       # 🌐 API Web Server (FastAPI Controllers)
    ├── __init__.py               # Server package initialization
    ├── app.py                    # FastAPI application factory, lifespan, CORS
    ├── config.py                 # Server runtime settings (Host, Port, etc.)
    ├── dependencies.py           # Dependency injection providers
    ├── main.py                   # Server startup runner (`python -m server.main`)
    ├── run_api_demo.py           # In-process simulation & verification script
    ├── routes/                   # Thin controllers
    │   ├── __init__.py
    │   ├── health_routes.py      # Health & liveness probe (/health)
    │   ├── ocr_routes.py         # OCR endpoints (/api/v1/ocr/*)
    │   └── rag_routes.py         # RAG endpoints placeholder (/api/v1/rag/*)
    └── tests/                    # Server integration test suite
```

---

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
cd /home/quan/projects/maivenpoint/AI/ChatbotOCR
source venv/bin/activate
```

### 2. Run the In-Process Verification Demo
```bash
python server/run_api_demo.py
```

### 3. Start the Unified API Web Server
```bash
# Via root launcher
python main.py --host 0.0.0.0 --port 8000

# Or via server module
python -m server.main --host 0.0.0.0 --port 8000
```
Interactive Swagger UI will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Direct CLI OCR
```bash
python main.py --ocr-file demo_output/sample_invoice.jpg --save-annotated demo_output/result.jpg
```

### 5. Run Automated Tests
```bash
# Run all tests (OCR domain tests + Server API integration tests)
pytest

# Or run tests per folder
pytest OCR/tests
pytest server/tests
```
