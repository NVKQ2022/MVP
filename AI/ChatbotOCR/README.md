# 🤖 ChatbotOCR: Support Knowledge & Visual Diagnostic Platform

ChatbotOCR is a unified, production-grade AI platform that diagnoses software issues from customer error screenshots. It combines high-accuracy Optical Character Recognition (PaddleOCR), structured entity extraction with PII redaction, dense vector search via PolyRAG and Milvus Lite, and grounded LLM resolution generation with anti-hallucination circuit breakers.

---

## 🏗️ Architecture Overview

The system is organized into three decoupled subsystems following Clean Architecture:
- **OCR Subsystem (`OCR/`)**: PaddleOCR-backed visual recognition pipeline featuring automatic 180° orientation correction, textline angle classification, and spatial reading order sorting.
- **RAG Subsystem (`RAG/`)**: PolyRAG 0.2.0 orchestration engine utilizing OpenAI `text-embedding-3-small` dense embeddings, embedded **Milvus Lite** vector storage (`./data/milvus_lite.db`), and grounded answer generation with source attribution.
- **Web & API Server (`server/`)**: FastAPI application providing an interactive web chat UI with drag-and-drop screenshot uploads, RESTful API endpoints, and live OpenAPI documentation.

---

## 🚀 How to Run This Project

### 1. Prerequisites
- **Python**: Python 3.10+ or Python 3.12 (tested on 3.12.3)
- **Git**
- **Operating System**: Linux, macOS, or Windows (WSL / Native PowerShell)

---

### 2. Environment Setup

#### Step 1: Clone the repository and navigate into the project directory
```bash
git clone https://github.com/NVKQ2022/MVP.git
cd MVP/AI/ChatbotOCR
```

#### Step 2: Create and activate a Python virtual environment
- **On Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **On Windows (PowerShell / Command Prompt):**
  ```powershell
  python -m venv venv
  venv\Scripts\activate
  ```

#### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

---

### 3. Environment Configuration (`.env`)

A ready-to-run `.env` file is included in the project root. If creating a new environment, copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Verify your `.env` contains the required keys:

```dotenv
# OpenAI / Azure OpenAI Configuration
OPENAI_API_KEY="your-openai-or-azure-key"
OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/v1"
MODEL_NAME="gpt-4o-mini"

# Embeddings & Vector DB
EMBEDDING_MODEL="text-embedding-3-small"
VECTOR_STORE_TYPE="milvus_lite"
MILVUS_DB_PATH="./data/milvus_lite.db"
MILVUS_COLLECTION_NAME="support_kb"
RAG_ENABLED=true

# OCR Model Configuration
OCR_VERSION="PP-OCRv4"
OCR_USE_ANGLE_CLS=false
OCR_MIN_CONFIDENCE=0.4
```

---

### 4. Knowledge Base Ingestion

The repository comes pre-indexed with 12 enterprise support articles in `data/milvus_lite.db`. If you modify or add documentation in `data/kb_documents/`, re-index them using the unified command:

- **Incremental Ingest / Verify:**
  ```bash
  python main.py ingest
  ```
- **Clean Force Re-ingest (Wipes existing collection and rebuilds from scratch):**
  ```bash
  python main.py ingest --force
  ```

---

### 5. Running the Application

ChatbotOCR provides multiple execution modes through a single unified entrypoint (`main.py`):

#### Mode A: Interactive Web Chat Application (Recommended)
Launch the web server using:
```bash
python main.py
```
*(Or specify custom host and port: `python main.py server --host 0.0.0.0 --port 8000`)*

Once running, access the interfaces in your browser:
- 💬 **Web Chat Interface**: [http://localhost:8000](http://localhost:8000)
  - Drag-and-drop or upload error screenshots (PNG, JPG, BMP, WEBP).
  - Inspect extracted text and bounding-box coordinates.
  - Review grounded troubleshooting steps, root cause analysis, and cited KB sources.
  - Interactive multi-turn follow-up chat.
- 📖 **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📋 **ReDoc API Reference**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

#### Mode B: Terminal Diagnosis CLI (End-to-End Image → Solution)
Diagnose any customer error screenshot directly from your command line without starting a browser:

```bash
python main.py diagnose data/sample_screenshots/kb-auth-001__01__clean_light.png
```

**Options:**
- `-p {naive,advanced,agentic}`: Choose the RAG strategy (`naive` is 1-shot fast retrieval; `advanced` uses query expansion and fusion).
- `-k <int>`: Number of knowledge chunks to retrieve (default: `2`).

**Example CLI Output:**
```text
=================================================================
🔍 STEP 1: Running OCR on 'kb-auth-001__01__clean_light.png'...
=================================================================
📝 Recognized OCR Text:
Error Code: AUTH-401 (HTTP 401 Unauthorized)
Invalid or expired authentication token.

=================================================================
📚 STEP 2: Querying PolyRAG Knowledge Base (NAIVE)...
=================================================================
🤖 Grounded Support Resolution:
Issue Identified: The customer received error AUTH-401 indicating an invalid or expired authentication token.
Likely Root Cause: The session token expired or the device clock drift caused token invalidation.
Recommended Fix:
  1. Have the user sign out and sign in again to refresh credentials.
  2. Verify system clock synchronization.
Cited Source: KB-AUTH-001.txt
```

---

#### Mode C: Standalone OCR Runner
Extract text and generate visual bounding-box annotations on any image:

```bash
python main.py ocr demo_output/sample_invoice.jpg --save-annotated demo_output/annotated_result.jpg
```

---

#### Mode D: Standalone PolyRAG Knowledge Query
Ask natural language questions directly against the indexed support database:

- **Single Query:**
  ```bash
  python main.py rag -q "How do I fix database deadlock errors?"
  ```
- **Interactive Terminal Support Session:**
  ```bash
  python main.py rag -i
  ```

---

### 6. Running the Automated Test Suite

ChatbotOCR includes a comprehensive test suite covering the image codec, spatial reading order sorter, OCR orchestrator, RAG vector retrieval, and FastAPI endpoints.

Run the test suite with:
```bash
pytest
```

To run domain-specific tests:
```bash
pytest OCR/tests       # Computer vision & OCR unit tests
pytest server/tests    # FastAPI REST endpoint integration tests
```

To test the 12-scenario RAG knowledge base pipeline:
```bash
python RAG/test_rag_pipeline.py
```

---

## 📁 Repository Structure

```text
ChatbotOCR/
├── main.py                           # 🚀 Unified CLI & Server entrypoint
├── requirements.txt                  # 📦 Dependencies manifest
├── pytest.ini                        # 🧪 Pytest configuration
├── .env.example                      # ⚙️ Environment variable template
├── README.md                         # 📖 Execution guide & project documentation
├── QUICK_START.txt                   # ⚡ Plaintext quick-start cheat sheet
├── SOLUTION_BRIEF.docx               # 📄 Executive architecture solution brief
│
├── OCR/                              # 🔍 Computer Vision & OCR Domain Subsystem
│   ├── services/
│   │   ├── ocr/                      # PaddleOCR & Mock backends + Factory
│   │   ├── orchestrator/             # OCROrchestratorService facade
│   │   ├── visualizer/               # Visual polygon annotator
│   │   └── codec/                    # Universal image codec (Base64/raw/RGBA)
│   ├── utils/                        # Spatial reading order sorter & loggers
│   └── tests/                        # OCR unit tests
│
├── RAG/                              # 🧠 Support Knowledge Base & PolyRAG Subsystem
│   ├── config.py                     # RAG & embedding settings
│   ├── cli.py                        # PolyRAG CLI runner
│   ├── services/                     # RAGEngine & Milvus Lite vector store
│   └── test_rag_pipeline.py          # 12-scenario end-to-end verification
│
├── server/                           # 🌐 FastAPI Web Application Subsystem
│   ├── app.py                        # Application factory & pre-warming lifespan
│   ├── static/                       # Web Chat UI (HTML5, CSS3, JS)
│   ├── routes/                       # REST controllers (/ocr, /pipeline, /health)
│   └── tests/                        # REST endpoint integration tests
│
├── data/
│   ├── kb_documents/                 # 📚 12 Support Knowledge Base Markdown docs
│   ├── sample_screenshots/           # 🖼️ Real-world error screenshot samples
│   └── milvus_lite.db/               # 🗄️ Embedded Milvus Lite SQLite database
│
└── scripts/
    ├── create_zip.py                 # 📦 Clean deliverable packager
    └── generate_solution_brief_docx.py # 📝 Solution brief DOCX generator
```
