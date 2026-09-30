# RFC Agentic RAG System - Clean Architecture

A production-grade Retrieval-Augmented Generation (RAG) and Agentic RAG system for networking RFC specifications, organized following **Clean Architecture** principles.

---

## Architecture Overview

This codebase is structured into four decoupled layers with explicit dependency inversion pointing inward towards the core domain:

```
                            +------------------------------------+
                            |         Presentation Layer         |
                            |   (FastAPI, CLI Entrypoints, Web)  |
                            +-----------------+------------------+
                                              |
                                              v
                            +-----------------+------------------+
                            |         Application Layer          |
                            | (Use Cases, Agent Loops, Workflows)|
                            +-----------------+------------------+
                                              |
                                              v
+-----------------------+   +-----------------+------------------+   +------------------------+
|  Infrastructure Layer |-->|           Domain Layer             |<--| Infrastructure Layer   |
| (ChromaDB, OpenAI LLM)|   |  (Entities, Values, Port Interfaces|   | (SentenceTransformers) |
+-----------------------+   +------------------------------------+   +------------------------+
```

### Layer Responsibilities

1. **Domain Layer (`src/domain/`)**
   - **Enterprise Entities**: `Document`, `Chunk`, `SearchResult`, `RAGResponse`, `AgentStep`, `AgentAction`, `AgentResponse`, `BenchmarkQuestion`, `BenchmarkResult`.
   - **Port Interfaces**:
     - `ChunkerInterface`: Abstraction for document chunking algorithms.
     - `EmbeddingModelInterface`: Abstraction for vector embeddings generation.
     - `VectorStoreInterface`: Abstraction for vector storage, cosine search, and management.
     - `LLMClientInterface`: Abstraction for chat and text completions with JSON parsing.
   - *Independent of any third-party framework or database library.*

2. **Application Layer (`src/application/`)**
   - **Use Cases**:
     - `IngestDocumentsUseCase`: Chunks text/files, computes embeddings, and indexes into vector store.
     - `NaiveRAGUseCase`: Standard single-round retrieve-then-read RAG pipeline.
     - `AgenticRAGUseCase`: Multi-round investigative retrieval with planning, query rewriting, deduplication, and fused self-reflection.
     - `ReActAgentUseCase`: Explicit Thought -> Action -> Observation loop using tools (`search_rfc`, `list_available_docs`).
     - `EvaluateBenchmarkUseCase`: Evaluates 20 RFC test questions across naive vs agentic RAG and calculates accuracy, gain, and latencies.
   - **Agent Tools (`src/application/tools/`)**: `RFCSearchTool`, `RFCInfoTool`.

3. **Infrastructure Layer (`src/infrastructure/`)**
   - **Adapters**:
     - `FixedSizeChunker`: Character-level chunker with configurable size and overlap.
     - `ChromaVectorStoreAdapter`: ChromaDB persistent client implementation.
     - `OpenAIEmbeddingAdapter`: OpenAI-compatible embedding API integration.
     - `SentenceTransformerEmbeddingAdapter`: Local Sentence-Transformers embeddings.
     - `OpenAILLMAdapter`: OpenAI / Azure OpenAI LLM completion and JSON parser adapter.
     - `Settings`: Environment configuration loader.

4. **Presentation Layer (`src/presentation/`)**
   - **Web API (`src/presentation/api/`)**: FastAPI application with `/health`, `/query`, `/rag`, `/agentic-rag`, and static UI serving.
   - **CLI Tools (`src/presentation/cli/`)**:
     - `start_agentic_rag.py`: Interactive CLI with observable action trajectory.
     - `run_benchmark.py`: 20-Question benchmark evaluator.
     - `info_chroma.py`: Chroma store status and inspection.
     - `clean_chroma.py`: Artifact cleaner for reproducible rebuilds.
     - `build_chunks.py`: Text doc chunking pipeline.
     - `build_embeddings.py`: Vector indexing pipeline.
     - `query.py`: Direct vector search tool.
     - `rag_query.py`: Naive RAG query tool.

5. **Composition Root (`src/container.py`)**
   - Factory container that wires interfaces to concrete adapters and assembles use cases.

---

## Directory Structure

```text
AI/RAG/
├── src/
│   ├── container.py                   # Dependency Injection Container (Composition Root)
│   ├── domain/                        # Domain entities & abstract ports
│   │   ├── entities/                  # Document, Chunk, SearchResult, RAGResponse, Agent
│   │   └── interfaces/                # Chunker, Embedding, VectorStore, LLM ports
│   ├── application/                   # Business use cases & workflows
│   │   ├── tools/                     # RFC search & info tools
│   │   └── use_cases/                 # Ingest, NaiveRAG, AgenticRAG, ReAct, Benchmark
│   ├── infrastructure/                # Concrete adapters
│   │   ├── chunking/                  # FixedSizeChunker
│   │   ├── config/                    # Settings & .env loading
│   │   ├── embedding/                 # OpenAI & SentenceTransformers adapters
│   │   ├── llm/                       # OpenAILLMAdapter
│   │   └── vector_store/              # ChromaVectorStoreAdapter
│   └── presentation/                  # Delivery mechanisms
│       ├── api/                       # FastAPI app, routes & schemas
│       └── cli/                       # CLI commands & runners
├── data/                              # RFC documents and chunks
│   ├── docs/                          # Raw RFC text files
│   └── chunks/                        # Generated JSON chunk data
├── docs/                              # Requirements, benchmark results, reflection
├── scripts/                           # Backward-compatible script wrappers
├── static/                            # Web frontend (index.html)
├── tests/                             # Unit & integration test suite
├── benchmark.py                       # Root benchmark entrypoint
├── agenticRag.py                      # Root agentic RAG entrypoint
├── startAgenticRag.py                 # Root CLI entrypoint
├── rag_service.py                     # Root Naive RAG service entrypoint
├── vectordb.py                        # Root VectorDB re-export
├── embedding.py                       # Root Embedding re-export
├── chunking.py                        # Root Chunking re-export
├── config.py                          # Root Config re-export
└── main.py                            # Root composition entrypoint
```

---

## Quickstart & Usage

### 1. Environment Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Key environment variables in `.env`:
- `ENDPOINT`: LLM API base URL (OpenAI or Azure OpenAI endpoint).
- `API_KEY`: API key.
- `MODEL_NAME`: Chat/completion model deployment name.
- `PROVIDER`: Embedding provider (`openai` or `hf`).
- `EMBEDDING_MODEL`: Embedding model (e.g. `text-embedding-3-small` or `all-MiniLM-L6-v2`).
- `CHROMA_PERSIST_DIR`: Directory for vector database (default: `chroma_db`).
- `CHROMA_COLLECTION`: Collection name (default: `rfc_docs`).

---

### 2. Running Agentic RAG (CLI)

Run a multi-hop question with complete observable action logging:

```bash
python startAgenticRag.py --query "When a DNS response exceeds the UDP size limit in RFC 1035, which header bit is set, and what TCP flags defined in RFC 793 are sent to initiate the fallback connection?"
```

Or invoke via clean architecture presentation module:

```bash
python -m src.presentation.cli.start_agentic_rag --top-k 3 --max-rounds 3
```

---

### 3. Running the 20-Question Benchmark

Run the full evaluation comparing Naive RAG vs Agentic RAG:

```bash
python benchmark.py
```

Or via module:

```bash
python -m src.presentation.cli.run_benchmark
```

---

### 4. Running the Web API & UI

Start the FastAPI server:

```bash
python scripts/server.py --port 8000
```

Or with `uvicorn`:

```bash
uvicorn src.presentation.api.app:app --host 0.0.0.0 --port 8000
```

Available endpoints:
- `GET /`: Serves web frontend (`static/index.html`).
- `GET /health`: System status, collection counts, and LLM connectivity.
- `POST /query`: Vector search over indexed RFC chunks.
- `POST /rag`: Naive retrieve-then-read RAG.
- `POST /agentic-rag`: Agentic RAG with iterative search and reflection.
- `GET /docs`: Interactive Swagger API documentation.

---

### 5. Running Tests

Run the comprehensive test suite with `pytest`:

```bash
pytest
```

The test suite covers:
- Domain layer entities and serialization.
- Chunking algorithms and edge cases.
- Mocked application use cases (Naive RAG, Agentic RAG, Ingestion, Benchmark).
- Composition container wiring.
- Web API endpoints with `TestClient`.
- Vector store backward compatibility.

---

## Backward Compatibility Guarantee

All original entrypoints, script names, and import paths continue to work without breaking:
- `main.py` -> `build_llm_client()`, `build_chunking_service()`, `build_vector_db()`, `build_rag_service()`
- `rag_service.py` -> `RAGService`
- `agenticRag.py` -> `AgenticRAGService`
- `vectordb.py` -> `VectorDB`, `ChromaVectorDB`
- `embedding.py` -> `EmbeddingService`, `OpenAIEmbeddingService`, `HFEmbeddingService`
- `chunking.py` -> `ChunkingService`, `FixedSizeChunkingService`
- `scripts/*` -> `server.py`, `info_chroma.py`, `clean_chroma.py`, `build_chunks.py`, `build_embeddings.py`, `query.py`, `rag_query.py`