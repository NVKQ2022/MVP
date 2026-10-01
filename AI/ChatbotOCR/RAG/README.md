# 🤖 RAG (Retrieval-Augmented Generation) Subsystem

This module powers knowledge base retrieval and grounded support answer generation using the [`PolyRAG`](https://github.com/NVKQ2022/PolyRAG) engine.

---

## 📁 Architecture & File Layout

```text
RAG/
├── __init__.py               # Package exports
├── config.py                 # RAG configuration settings (.env driven)
├── cli.py                    # Interactive and one-shot terminal query tool
├── test_rag_pipeline.py      # End-to-end verification script for all RAG pipelines
├── HOW_TO_USE.md             # Complete package reference & guide for PolyRAG
└── services/
    ├── __init__.py
    └── rag_engine.py         # PolyRAG engine orchestrator (ChromaDB + SentenceTransformers)
```

---

## 📚 Knowledge Base Storage

The primary knowledge base documents live directly in:
`data/kb_documents/`
- `KB-AUTH-001.txt` (Invalid or expired authentication token)
- `KB-AUTH-002.txt` (Customer account is locked)
- `KB-AUTH-003.txt` (Email address has not been verified)
- `KB-NET-001.txt` (Connection timed out)
- `KB-NET-002.txt` (Service temporarily unavailable)
- `KB-NET-003.txt` (DNS resolution failed)
- `KB-DB-001.txt` (Duplicate key violation)
- `KB-DB-002.txt` (Database connection failed)
- `KB-DB-003.txt` (Database deadlock detected)
- `KB-FILE-001.txt` (Uploaded file is too large)
- `KB-FILE-002.txt` (Unsupported file type)
- `KB-GEN-001.txt` (Resource not found)

---

## 🚀 Quick Usage

### 1. One-Shot Question via CLI:
```bash
python RAG/cli.py -q "AUTH-401 invalid token"
```

### 2. Interactive Terminal Chat:
```bash
python RAG/cli.py -i
```

### 3. Re-index Knowledge Documents:
```bash
python RAG/cli.py --ingest
```

### 4. Run Full Pipeline Verification:
```bash
python RAG/test_rag_pipeline.py
```
