# PolyRAG Integration Brief: ChatbotOCR

This document provides a concise technical brief on **PolyRAG** and how it is utilized within the **ChatbotOCR** enterprise support assistant.

---

## 1. Overview & Role in the Project

[PolyRAG](https://github.com/NVKQ2022/PolyRAG) (`polyrag==0.2.0`) is an open-source, modular Retrieval-Augmented Generation (RAG) framework designed for extensible, production-ready search and generation pipelines.

In **ChatbotOCR**, PolyRAG powers the entire **RAG Domain Subsystem** (`RAG/`). It connects the structured diagnostic output from the OCR/Computer Vision layer to an embedded vector knowledge base and synthesizes grounded, factual troubleshooting solutions for end users.

Following project constraints, this system focuses strictly on **`NaiveRAG`** (a clean, high-performance retrieve-then-read pipeline).

---

## 2. Architectural Alignment: LangChain-Native (PolyRAG 0.2.0)

With version **0.2.0**, PolyRAG transitioned to a modern **LangChain-native** architecture. Instead of bespoke or proprietary interfaces, PolyRAG adopts standard abstractions from the LangChain ecosystem (`langchain-core`, `langchain-milvus`, `langchain-huggingface`, `langchain-openai`):

- **`VectorStore`**: Standard vector repository interface.
- **`Embeddings`**: Universal interface for dense vector representation.
- **`BaseChatModel`**: Standard chat generation interface.
- **`TextSplitter`**: Structural document chunking.

This allows PolyRAG to act as a lightweight, clean orchestrator with plug-and-play interchangeability.

---

## 3. Core PolyRAG Components Used in ChatbotOCR

All RAG functionality is coordinated through [`RAGEngine`](file:///home/quan/projects/maivenpoint/AI/ChatbotOCR/RAG/services/rag_engine.py):

```text
Extracted OCR Issue (Error Code / Symptoms)
                    │
                    ▼
     PolyRAG Embeddings Resolver
       (all-MiniLM-L6-v2 / 384-d)
                    │
                    ▼
     PolyRAG MilvusLiteVectorStore
         (./data/milvus_lite.db)
                    │
                    ▼
          Hybrid Re-ranking
     (Cosine Sim + Exact-Code Boost)
                    │
                    ▼
         PolyRAG NaiveRAG Pipeline
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
   Score ≥ 0.45           Score < 0.45
 Azure OpenAI (LLM)   Circuit Breaker Fallback
 (Grounded Solution)   (Diagnostic Questions)
```

### 3.1 Embedded Vector Store (`MilvusLiteVectorStore`)
- Extends `langchain_milvus.Milvus` to provide custom management utilities (`count()`, `clear()`, `peek()`).
- Runs embedded inside the application process using **Milvus Lite**, persisting vectors to `./data/milvus_lite.db`.
- **Zero-infrastructure deployment**: requires no Docker containers or standalone servers for local execution, while maintaining 100% API compatibility with distributed enterprise Milvus clusters.

### 3.2 Embedding Model Resolver (`resolve_embedding_model`)
- Uses PolyRAG's dynamic resolver to initialize `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors via `HuggingFaceEmbeddings`).
- Automatically supports OpenAI embedding models (`text-embedding-3-small`) when API credentials are provided.

### 3.3 Structural Text Chunker (`RecursiveCharacterChunker`)
- Subclasses LangChain's `RecursiveCharacterTextSplitter`.
- Configured with a `chunk_size` of 500 characters and `chunk_overlap` of 50 characters, preserving Markdown structural integrity (headers, lists, callouts).

### 3.4 LLM Client Resolver (`resolve_llm_client`)
- Initializes Azure OpenAI / OpenAI chat models (`ChatOpenAI`) via PolyRAG's factory pattern.
- Injects a strict support prompt enforcing that responses are grounded solely in the retrieved context.

### 3.5 Pipeline Engine (`NaiveRAG`)
- Coordinates the single-turn retrieve-then-read loop:
  - `naive_rag.ingest_text(...)`: chunks, embeds, and indexes documentation.
  - `naive_rag.retrieve(...)`: executes similarity search.
  - `naive_rag.execute(...)`: generates the grounded answer with citations and latency metrics.

---

## 4. Knowledge Ingestion Flow

The knowledge base is composed of 12 production-grade Markdown articles located in [`data/kb_documents/`](file:///home/quan/projects/maivenpoint/AI/ChatbotOCR/data/kb_documents/):

1. **Document Discovery**: Scans Markdown files across categories (Authentication, Database, Network, Storage, Platform).
2. **Metadata Parsing**: Extracts article metadata headers (`article_id`, `product`, `module`, `error_codes`, `symptoms`, `severity`).
3. **PolyRAG Ingestion**: Calls `naive_rag.ingest_text()` to split each document into context chunks and store them in Milvus Lite with structured payload metadata.

Ingestion can be triggered dynamically via API (`POST /api/pipeline/ingest`) or CLI (`python -m RAG.cli ingest`).

---

## 5. Hybrid Retrieval & Guardrails

PolyRAG's standard retrieval in ChatbotOCR is augmented with enterprise guardrails:

1. **Exact Error-Code Match Bonus**:
   $$\text{FinalScore} = \min\left(1.0,\; 0.75 \times \text{CosineSimilarity} + \text{ExactMatchBonus}\right)$$
   If an extracted error code (e.g. `AUTH-401`, `NET-502`) matches an article's metadata, an **ExactMatchBonus of +0.25** is awarded, ensuring direct diagnostic hits rank #1 over generic matches.

2. **Anti-Hallucination Circuit Breaker**:
   - If the top retrieved article achieves $\text{score} \ge 0.45$: PolyRAG invokes the LLM to format a structured 5-part guide (*Issue Identified*, *Root Cause*, *Recommended Fix Steps*, *Verification Steps*, *Source Citations*).
   - If no article achieves $\text{score} \ge 0.45$: The LLM generation is completely bypassed. The system returns a safe, deterministic questionnaire requesting logs and reproduction steps.

---

## 6. Key Benefits of Using PolyRAG

| Benefit | How It Solves Project Requirements |
|---|---|
| **LangChain Native** | Zero custom glue code; leverages battle-tested industry standard components. |
| **Clean Decoupling** | Keeps OCR computer vision entirely separate from semantic NLP and retrieval. |
| **Predictable Latency** | NaiveRAG delivers sub-second answers (150–300ms vector lookup) without agentic multi-turn delays. |
| **Seamless Scalability** | Migration from Milvus Lite (local file) to Milvus Standalone (Docker) requires changing only one connection URI. |
| **Auditability** | Every generated answer includes source document references and confidence scores for support verification. |
