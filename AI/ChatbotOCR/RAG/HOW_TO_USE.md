# PolyRAG — How To Use

> **Package**: `polyrag==0.1.5`
> **Install**: `pip install git+https://github.com/NVKQ2022/PolyRAG.git`
> **Only dependency**: `pydantic>=2.0.0` (everything else is optional based on what you use)
> **Vector Store Support**: ChromaDB (persistent) + InMemory (transient) + Milvus / Milvus Lite (v0.1.5+).

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Installation & Dependencies](#2-installation--dependencies)
3. [Quick Start (5-Minute Setup)](#3-quick-start-5-minute-setup)
4. [Core Concepts](#4-core-concepts)
5. [Entry Points — 3 Ways to Use PolyRAG](#5-entry-points--3-ways-to-use-polyrag)
6. [Document Ingestion](#6-document-ingestion)
7. [Retrieval (Search)](#7-retrieval-search)
8. [RAG Pipelines](#8-rag-pipelines)
9. [Component Reference](#9-component-reference)
10. [Dependency Injection (DI Container)](#10-dependency-injection-di-container)
11. [Custom Components (Extending PolyRAG)](#11-custom-components-extending-polyrag)
12. [Configuration & Environment Variables](#12-configuration--environment-variables)
13. [Data Models](#13-data-models)
14. [Exception Hierarchy](#14-exception-hierarchy)
15. [Known Issues & Gotchas](#15-known-issues--gotchas)
16. [Complete API Reference](#16-complete-api-reference)

---

## 1. Architecture Overview

PolyRAG follows a **modular, pluggable architecture** with clear interfaces (ports) and swappable adapters:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Entry Points                                │
│  PolyRAG (App Context)  │  RAGService (Facade)  │  Container   │
├─────────────────────────────────────────────────────────────────┤
│                     RAG Pipelines                               │
│  NaiveRAG  │  AdvancedRAG  │  AgenticRAG  │  ReActAgent        │
├─────────────────────────────────────────────────────────────────┤
│                     Core Interfaces (ABC)                       │
│  BaseChunker │ BaseEmbeddingModel │ BaseVectorStore │ BaseLLM   │
├─────────────────────────────────────────────────────────────────┤
│                     Concrete Adapters                           │
│  Chunkers:    RecursiveCharacterChunker, FixedSizeChunker       │
│  Embeddings:  SentenceTransformerEmbedding, OpenAIEmbedding     │
│  VectorStore: ChromaVectorStore, InMemoryVectorStore            │
│  LLM:        OpenAILLM (OpenAI / Azure / compatible)            │
└─────────────────────────────────────────────────────────────────┘
```

**Key design principle**: Every component is an implementation of an abstract interface (`BaseChunker`, `BaseEmbeddingModel`, `BaseVectorStore`, `BaseLLMClient`). You can swap any component without changing the pipeline code.

---

## 2. Installation & Dependencies

### Core Package

```bash
pip install git+https://github.com/NVKQ2022/PolyRAG.git
```

### Optional Dependencies (install based on what you use)

```bash
# For local embeddings (SentenceTransformerEmbedding)
pip install sentence-transformers

# For OpenAI LLM & embeddings
pip install openai

# For ChromaDB persistent storage
pip install chromadb
```

### All-in-one for this project

```bash
pip install git+https://github.com/NVKQ2022/PolyRAG.git sentence-transformers openai chromadb
```

---

## 3. Quick Start (5-Minute Setup)

### Minimal Example — InMemory + Sentence Transformers + OpenAI

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

from polyrag import PolyRAG

# 1. Create the app (InMemory store, all-MiniLM-L6-v2 embeddings, gpt-4o-mini LLM)
app = PolyRAG.create(model_name="gpt-4o-mini")

# 2. Ingest some knowledge
app.ingest_text(
    text="Error AUTH-401 means the authentication token is invalid or expired. "
         "Resolution: verify auth status, check token expiry, refresh session.",
    source="auth_troubleshooting.md",
    metadata={"category": "authentication", "error_code": "AUTH-401"},
)

# 3. Query
response = app.query("What does AUTH-401 mean?", top_k=3)
print(response.answer)
print(response.sources)
```

### With ChromaDB Persistence

```python
from polyrag import PolyRAG

app = PolyRAG.create(
    model_name="gpt-4o-mini",
    embedding_model="all-MiniLM-L6-v2",
    persist_dir="./chroma_db",          # ChromaDB data stored here
    collection_name="support_kb",
)

# Ingest once, persists to disk
app.ingest_text("...", source="doc.md")

# Later, reload from persistence (same persist_dir)
app2 = PolyRAG.create(persist_dir="./chroma_db", collection_name="support_kb")
response = app2.query("What is error 401?")
```

> **⚠ Known Bug**: `PolyRAG.create()` and `RAGService.create()` pass `persist_path=` to
> `ChromaVectorStore`, but its constructor expects `persist_directory=`. This will cause a
> `TypeError`. **Workaround**: Create `ChromaVectorStore` manually and inject it
> (see [Section 5.3](#53-container--manual-wiring)).

---

## 4. Core Concepts

### 4.1 Document → Chunk → Embed → Store → Search → Generate

```
Document (raw text)
    ↓ Chunker.chunk()
Chunks (list[str])
    ↓ EmbeddingModel.embed_batch()
Vectors (list[list[float]])
    ↓ VectorStore.add_documents()
Stored in DB
    ↓ VectorStore.search(query_vector)
SearchResults
    ↓ LLM.complete(prompt + context)
Answer
```

### 4.2 Key Data Flow

| Step | Method | Input | Output |
|------|--------|-------|--------|
| Chunk | `chunker.chunk(text)` | `str` | `list[str]` |
| Embed | `embedding.embed_batch(texts)` | `list[str]` | `list[list[float]]` |
| Store | `vector_store.add_documents(vectors, docs)` | vectors + doc dicts | persisted |
| Search | `vector_store.search(query_vector, top_k)` | query vector | `list[dict]` with `score`, `distance`, `document` |
| Generate | `llm.complete(prompt)` | prompt string | answer string |

---

## 5. Entry Points — 3 Ways to Use PolyRAG

### 5.1 `PolyRAG` — Application Context (Recommended)

The main entry point. Acts as a factory + orchestrator.

```python
from polyrag import PolyRAG

# Option A: From environment variables
app = PolyRAG.from_env(
    persist_dir="./chroma_db",      # default: "./chroma_db"
    collection_name="documents",    # default: "documents"
    embedding_model="all-MiniLM-L6-v2",  # default
)

# Option B: Explicit configuration
app = PolyRAG.create(
    model_name="gpt-4o-mini",       # LLM model
    embedding_model="all-MiniLM-L6-v2",
    persist_dir="./chroma_db",      # None = InMemory
    collection_name="support_kb",
)

# Option C: Full manual control
from polyrag import (
    RecursiveCharacterChunker,
    SentenceTransformerEmbedding,
    ChromaVectorStore,
    OpenAILLM,
)
app = PolyRAG(
    chunker=RecursiveCharacterChunker(chunk_size=500, chunk_overlap=50),
    embedding_model=SentenceTransformerEmbedding(model_name="all-MiniLM-L6-v2"),
    vector_store=ChromaVectorStore(persist_directory="./my_db", collection_name="kb"),
    llm_client=OpenAILLM(model_name="gpt-4o-mini"),
)
```

**PolyRAG methods:**

| Method | Description |
|--------|-------------|
| `ingest_text(text, source, metadata)` | Chunk + embed + store text |
| `ingest(text, source, metadata)` | Alias for `ingest_text` |
| `ingest_file(file_path, metadata)` | Read file → ingest |
| `ingest_directory(dir_path, glob_pattern, metadata)` | Recursively ingest all matching files |
| `retrieve(query, top_k)` | Embed query → vector search → return results |
| `format_context(search_results)` | Format results into context string |
| `query(question, top_k)` | End-to-end: retrieve + generate answer (uses NaiveRAG) |
| `create_naive_rag()` | Build NaiveRAG pipeline |
| `create_advanced_rag(top_k, num_expanded_queries, ...)` | Build AdvancedRAG pipeline |
| `create_agentic_rag(top_k, max_rounds, verbose)` | Build AgenticRAG pipeline |
| `create_react_agent(max_steps, default_top_k, verbose)` | Build ReActAgent pipeline |
| `create_agentic_service(top_k, max_rounds, verbose)` | Build AgenticRAGService facade |

### 5.2 `RAGService` — Backward-Compatible Facade

Extends `PolyRAG` with backward-compatible attribute names. Use if you're migrating from an older PolyRAG version.

```python
from polyrag import RAGService

# From env
svc = RAGService.from_env(
    persist_dir="./chroma_db",
    collection_name="rfc_documents",
)

# Or create explicitly
svc = RAGService.create(
    model_name="gpt-4o-mini",
    embedding_model="all-MiniLM-L6-v2",
    persist_dir="./chroma_db",
    collection_name="support_kb",
)

# Same API as PolyRAG
svc.ingest_text("...", source="doc.md")
response = svc.query("question?", top_k=5)

# Access internal components directly
svc.chunking_service    # → BaseChunker
svc.embedding_service   # → BaseEmbeddingModel
svc.vector_db           # → BaseVectorStore
svc.llm_client          # → BaseLLMClient
svc.client              # → raw OpenAI client object
```

### 5.3 `Container` — Manual DI Wiring

For full control over dependency injection:

```python
from polyrag import (
    Container,
    RecursiveCharacterChunker,
    SentenceTransformerEmbedding,
    ChromaVectorStore,
    InMemoryVectorStore,
    OpenAILLM,
)
from polyrag.core.interfaces import (
    BaseChunker,
    BaseEmbeddingModel,
    BaseVectorStore,
    BaseLLMClient,
)

# Build container manually
container = Container()
container.register_instance(BaseChunker, RecursiveCharacterChunker(chunk_size=400))
container.register_instance(BaseEmbeddingModel, SentenceTransformerEmbedding())
container.register_instance(BaseVectorStore, InMemoryVectorStore())
container.register_instance(BaseLLMClient, OpenAILLM(model_name="gpt-4o-mini"))

# Build pipelines from container
naive = container.build_naive_rag()
advanced = container.build_advanced_rag(top_k=5, num_expanded_queries=3)
agentic = container.build_agentic_rag(top_k=3, max_rounds=2, verbose=True)
react = container.build_react_agent(max_steps=4, verbose=True)

# Or build app/service from container
app = container.build_app()          # → PolyRAG instance
service = container.build_service()  # → RAGService instance
```

**Container shortcuts:**

```python
# From env variables
container = Container.from_env(persist_dir="./db", collection_name="docs")

# With custom components
container = Container.create(
    chunker=my_chunker,
    embedding_model=my_embedder,
    vector_store=my_store,
    llm_client=my_llm,
)
```

---

## 6. Document Ingestion

### 6.1 Ingest Raw Text

```python
docs = app.ingest_text(
    text="Error AUTH-401: Invalid or expired authentication token...",
    source="auth_guide.md",           # Identifies the source document
    metadata={                         # Extra metadata stored alongside chunks
        "category": "authentication",
        "error_code": "AUTH-401",
        "product": "Admin Portal",
    },
)
# Returns: list[dict] — each dict is a stored chunk document:
# [
#     {"text": "Error AUTH-401...", "source": "auth_guide.md", "chunk_id": 0, "category": "authentication", ...},
#     {"text": "...", "source": "auth_guide.md", "chunk_id": 1, ...},
# ]
```

### 6.2 Ingest a File

```python
docs = app.ingest_file(
    file_path="./data/knowledge_base/auth_troubleshooting.md",
    metadata={"category": "authentication"},
)
# Source is auto-set to the filename
```

### 6.3 Ingest a Directory

```python
docs = app.ingest_directory(
    dir_path="./data/knowledge_base/",
    glob_pattern="*.md",              # Default: "*.txt"
    metadata={"source_type": "kb"},
)
# Recursively finds all matching files and ingests them
```

### 6.4 What Happens During Ingestion

```
text → chunker.chunk(text) → list[str] chunks
     → embedding.embed_batch(chunks) → list[list[float]] vectors
     → vector_store.add_documents(vectors, documents)
```

Each chunk is stored as a document dict with at minimum:
- `text` — the chunk text
- `source` — origin filename/identifier
- `chunk_id` — sequential integer (0, 1, 2, ...)
- `_id` — auto-generated UUID for the store
- Plus any extra `metadata` fields you provided

---

## 7. Retrieval (Search)

### 7.1 Basic Retrieval

```python
results = app.retrieve(query="authentication error 401", top_k=5)
```

### 7.2 Result Format

Each result is a dict:

```python
{
    "score": 0.87,          # Cosine similarity (1.0 = identical)
    "distance": 0.13,       # 1.0 - score
    "document": {
        "_id": "auth_guide_0_a1b2c3d4",
        "text": "Error AUTH-401 means...",
        "source": "auth_guide.md",
        "chunk_id": 0,
        "category": "authentication",    # your metadata
        "error_code": "AUTH-401",        # your metadata
    }
}
```

### 7.3 Format Context for LLM

```python
context_str = app.format_context(results)
# Returns formatted string:
# Source: auth_guide.md#0
# Error AUTH-401 means...
#
# ---
#
# Source: auth_guide.md#1
# Resolution: verify auth status...
```

---

## 8. RAG Pipelines

### 8.1 NaiveRAG — Simple Retrieve-then-Read

The simplest pipeline. One-shot retrieval + generation.

```python
pipeline = app.create_naive_rag()
# Or directly:
response = app.query("What is AUTH-401?", top_k=5)  # Uses NaiveRAG internally
```

**Flow**: `embed query → search top_k → format context → LLM.complete(prompt + context)`

**Prompt template** (hardcoded):
```
Use the following context to answer the question.
If the answer is not in the context, state that the context lacks sufficient information.

Context:
{context}

Question: {question}
Answer with citations where possible:
```

**Response**: `RAGResponse` (see [Data Models](#13-data-models))

### 8.2 AdvancedRAG — Multi-Query Expansion + RRF Fusion

```python
pipeline = app.create_advanced_rag(
    top_k=5,                    # Results per query
    num_expanded_queries=3,     # LLM generates N alternative queries
    min_relevance_score=0.0,    # Filter threshold
    verbose=False,
)
response = pipeline.execute("What happens with expired tokens?", top_k=5)
```

**Flow**:
1. **Pre-Retrieval**: LLM generates N diverse search queries from the original question
2. **Multi-Query Retrieval**: Each query is embedded and searched separately
3. **Post-Retrieval**: Reciprocal Rank Fusion (RRF) merges and re-ranks results
4. **Generation**: LLM synthesizes answer from fused context

**RRF Formula**: `score(doc) = Σ(1 / (k + rank))` where `k=60` (default)

### 8.3 AgenticRAG — Multi-Round Retrieval with Reflection

```python
pipeline = app.create_agentic_rag(
    top_k=3,          # Results per round
    max_rounds=2,     # Max retrieval rounds
    verbose=True,     # Print agent actions
)
response = pipeline.execute("Troubleshoot AUTH-401 error on Admin Portal")
```

**Flow**:
1. **Planning**: LLM decides if retrieval is needed → rewrites query
2. **Multi-Round Loop**:
   - Retrieve top-k chunks
   - Deduplicate against previously seen chunks
   - **Fused Reflection**: LLM evaluates if evidence is sufficient AND generates answer in one call
   - If insufficient → LLM generates `next_query` → loop continues
3. **Fallback**: If no answer after all rounds → one final LLM generation call

**Agent Actions** (logged when `verbose=True`):
- `PLANNING` — decides retrieval needed + rewrites query
- `VECTOR_SEARCH` — retrieves chunks
- `DEDUPLICATION` — removes duplicate chunks
- `REFLECTION_AND_EVALUATION` — evaluates sufficiency + may generate answer
- `QUERY_REFINEMENT` — rewrites query for next round
- `DIRECT_ANSWER` — answers without retrieval (for greetings etc.)

### 8.4 ReActAgent — Thought-Action-Observation Loop

```python
agent = app.create_react_agent(
    max_steps=4,        # Max reasoning steps
    default_top_k=5,    # Default search results
    verbose=True,
)
response = agent.execute("What causes database deadlock errors?")
# Returns: AgentResponse (not RAGResponse!)
```

**Flow**: Structured JSON reasoning loop:
```
Step 1: {"thought": "I need to find...", "action": "search", "action_input": {"query": "...", "top_k": 5}}
  → Observation: Retrieved 5 chunks: [source#0]: ...
Step 2: {"thought": "I found...", "action": "final_answer", "action_input": {"answer": "...", "confidence": 0.95}}
```

**Available Tools**:
- `search` — Vector search. Input: `{"query": "...", "top_k": N}`
- `list_docs` — Inspect collection stats. Input: `{}`
- `final_answer` — Emit answer. Input: `{"answer": "...", "confidence": 0.0-1.0}`

**Response**: `AgentResponse` with `trajectory` (list of reasoning steps), `retrieved_evidence`, etc.

### 8.5 AgenticRAGService — Service Facade for AgenticRAG

```python
# Create from app
agentic_svc = app.create_agentic_service(top_k=3, max_rounds=2, verbose=True)

# Or from RAGService
svc = RAGService.create(...)
agentic_svc = svc.create_agentic_rag(top_k=3)  # Also returns AgenticRAGService

# Or standalone from env
from polyrag import AgenticRAGService
agentic_svc = AgenticRAGService.from_env(
    top_k=3, max_rounds=2, verbose=True,
    persist_dir="./chroma_db", collection_name="docs",
)

# Query
response = agentic_svc.query("What is AUTH-401?")

# Individual steps (for debugging)
decision = agentic_svc.decide_retrieval("hello")
# → {"retrieval_needed": false, "query": "hello", "reason": "greeting"}

answer = agentic_svc.direct_answer("What is RAG?")
# → "RAG stands for Retrieval-Augmented Generation..."

reflection = agentic_svc.reflect_and_evaluate("question", "context", round_number=1)
# → {"enough": true, "confidence": 0.9, "answer": "...", ...}
```

---

## 9. Component Reference

### 9.1 Chunkers

#### `RecursiveCharacterChunker` (default)

Splits text hierarchically along natural boundaries (`\n\n`, `\n`, `. `, ` `, ``).

```python
from polyrag import RecursiveCharacterChunker

chunker = RecursiveCharacterChunker(
    chunk_size=550,                   # Max characters per chunk (default: 550)
    chunk_overlap=35,                 # Overlap between chunks (default: 35)
    separators=["\n\n", "\n", ". ", " ", ""],  # default
    drop_empty=True,                  # Skip empty chunks (default: True)
)
chunks = chunker.chunk("long document text...")
# → ["chunk 1...", "chunk 2...", ...]
```

#### `FixedSizeChunker`

Simple sliding window character chunker.

```python
from polyrag import FixedSizeChunker

chunker = FixedSizeChunker(
    chunk_size=550,      # Characters per chunk
    chunk_overlap=35,    # Overlap
    drop_empty=True,
)
chunks = chunker.chunk("text...")
```

### 9.2 Embedding Models

#### `SentenceTransformerEmbedding` (default, local, FREE)

```python
from polyrag import SentenceTransformerEmbedding

emb = SentenceTransformerEmbedding(model_name="all-MiniLM-L6-v2")
# Requires: pip install sentence-transformers

emb.dim            # → 384 (dimension of all-MiniLM-L6-v2)
emb.embed_text("hello")        # → list[float] of length 384
emb.embed_batch(["a", "b"])    # → list[list[float]], batch processing
```

**Popular models:**

| Model | Dimensions | Speed | Quality |
|-------|-----------|-------|---------|
| `all-MiniLM-L6-v2` | 384 | ⚡ Fast | Good |
| `all-mpnet-base-v2` | 768 | Medium | Better |
| `all-MiniLM-L12-v2` | 384 | Fast | Good+ |

#### `OpenAIEmbedding` (API, paid)

```python
from polyrag import OpenAIEmbedding

emb = OpenAIEmbedding(
    model_name="text-embedding-3-small",  # default
    api_key="sk-...",        # or use OPENAI_API_KEY env var
    base_url=None,           # for Azure/compatible endpoints
)
emb.dim   # → 1536
```

**Supported models:** `text-embedding-3-small` (1536d), `text-embedding-3-large` (3072d), `text-embedding-ada-002` (1536d)

### 9.3 Vector Stores

#### `ChromaVectorStore` (persistent, recommended for production)

```python
from polyrag import ChromaVectorStore

store = ChromaVectorStore(
    persist_directory="./chroma_db",    # Directory for persistent storage
    collection_name="support_kb",      # Collection name
)
# Uses cosine similarity (hnsw:space = cosine)
# Requires: pip install chromadb
```

**Methods:**

```python
store.add_documents(vectors, documents, batch_size=5000)
store.search(query_vector, top_k=5)  # → list[dict]
store.count()                         # → int
store.peek(limit=5)                   # → preview records
store.clear()                         # → delete all records
```

#### `InMemoryVectorStore` (transient, for testing/development)

```python
from polyrag import InMemoryVectorStore

store = InMemoryVectorStore()
# Zero dependencies, pure Python cosine similarity
# Data lost when process exits
```

Same interface as `ChromaVectorStore`.

### 9.4 LLM Clients

#### `OpenAILLM`

```python
from polyrag import OpenAILLM

llm = OpenAILLM(
    model_name="gpt-4o-mini",    # default
    api_key="sk-...",             # or OPENAI_API_KEY env var
    base_url=None,                # for Azure / local / compatible endpoints
    client=None,                  # or pass a pre-built OpenAI() client
)

# Text completion
answer = llm.complete("What is RAG?")

# JSON completion (auto-parses JSON from LLM output)
data = llm.complete_json("Return JSON: {\"answer\": \"...\"}")
# → dict (parsed JSON)

# Chat completion
answer = llm.chat([
    {"role": "system", "content": "You are a support assistant."},
    {"role": "user", "content": "What is error 401?"},
])

llm.model_name  # → "gpt-4o-mini"
```

---

## 10. Dependency Injection (DI Container)

The `Container` provides a lightweight IoC container for wiring components.

```python
from polyrag import Container
from polyrag.core.interfaces import BaseChunker, BaseEmbeddingModel, BaseVectorStore, BaseLLMClient

container = Container()

# Register instances (singletons)
container.register_instance(BaseChunker, my_chunker)
container.register_instance(BaseEmbeddingModel, my_embedder)
container.register_instance(BaseVectorStore, my_store)
container.register_instance(BaseLLMClient, my_llm)

# Resolve
chunker = container.resolve(BaseChunker)

# Check registration
container.is_registered(BaseChunker)  # → True

# Register lazy factory (singleton by default)
container.register_factory(BaseVectorStore, lambda c: ChromaVectorStore(...), singleton=True)

# Build pipelines
naive = container.build_naive_rag()
advanced = container.build_advanced_rag(top_k=5, num_expanded_queries=3)
agentic = container.build_agentic_rag(top_k=3, max_rounds=2, verbose=True)
react = container.build_react_agent(max_steps=4, verbose=True)
app = container.build_app()          # → PolyRAG
service = container.build_service()  # → RAGService
```

---

## 11. Custom Components (Extending PolyRAG)

### 11.1 Custom Chunker

```python
from polyrag.core.interfaces import BaseChunker

class SentenceChunker(BaseChunker):
    def chunk(self, text: str) -> list[str]:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
```

### 11.2 Custom Embedding Model

```python
from polyrag.core.interfaces import BaseEmbeddingModel

class MyEmbedding(BaseEmbeddingModel):
    @property
    def dim(self) -> int:
        return 768

    def embed_text(self, text: str) -> list[float]:
        # your embedding logic
        ...

    def embed_batch(self, texts: list[str], batch_size: int = 128) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]
```

### 11.3 Custom Vector Store (e.g., Milvus)

```python
from polyrag.core.interfaces import BaseVectorStore
from typing import Any

class MilvusVectorStore(BaseVectorStore):
    """Example Milvus implementation of BaseVectorStore."""

    def __init__(self, uri: str, collection_name: str, dim: int):
        from pymilvus import MilvusClient
        self.client = MilvusClient(uri=uri)
        self.collection_name = collection_name
        self.dim = dim
        # Create collection if not exists...

    def clear(self) -> None:
        self.client.drop_collection(self.collection_name)

    def add_documents(
        self,
        vectors: list[list[float]],
        documents: list[dict[str, Any]],
        batch_size: int = 5000,
    ) -> None:
        data = []
        for vec, doc in zip(vectors, documents):
            data.append({"vector": vec, **doc})
        self.client.insert(collection_name=self.collection_name, data=data)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=["text", "source", "chunk_id"],
        )
        output = []
        for hit in results[0]:
            output.append({
                "score": 1.0 - hit["distance"],
                "distance": hit["distance"],
                "document": hit["entity"],
            })
        return output

    def count(self) -> int:
        stats = self.client.get_collection_stats(self.collection_name)
        return stats["row_count"]

    def peek(self, limit: int = 5) -> Any:
        return self.client.query(self.collection_name, limit=limit)
```

### 11.4 Using Custom Components

```python
from polyrag import PolyRAG

milvus_store = MilvusVectorStore(
    uri="./milvus_lite.db",
    collection_name="support_kb",
    dim=384,
)

app = PolyRAG(
    vector_store=milvus_store,
    # other components use defaults
)
```

---

## 12. Configuration & Environment Variables

| Variable | Default | Used By | Description |
|----------|---------|---------|-------------|
| `OPENAI_API_KEY` | (required) | `OpenAILLM`, `OpenAIEmbedding` | OpenAI API key |
| `MODEL_NAME` | `gpt-4o-mini` | `Container.from_env()`, `RAGService.from_env()` | LLM model name |
| `OPENAI_BASE_URL` | (optional) | `OpenAILLM` | Custom API endpoint (Azure, local, etc.) |

**Note**: PolyRAG does NOT use `python-dotenv` to auto-load `.env` files. You need to load them yourself:

```python
from dotenv import load_dotenv
load_dotenv()

from polyrag import PolyRAG
app = PolyRAG.from_env()
```

---

## 13. Data Models

### `Document`

```python
@dataclass
class Document:
    source: str                           # Source file/identifier
    text: str                             # Document text
    metadata: dict[str, Any] = {}         # Extra metadata
    doc_id: str | None = None             # Optional document ID
```

### `Chunk`

```python
@dataclass
class Chunk:
    source: str
    chunk_id: int | str
    text: str
    metadata: dict[str, Any] = {}
    chunk_uuid: str | None = None

    @property
    def identifier(self) -> str:          # "source#chunk_id"
    def to_dict(self) -> dict[str, Any]:  # Flatten to dict
```

### `SearchResult`

```python
@dataclass
class SearchResult:
    score: float                          # Cosine similarity (0-1)
    distance: float                       # 1 - score
    document: dict[str, Any] = {}         # The stored document dict

    @property
    def source(self) -> str:
    @property
    def chunk_id(self) -> Any:
    @property
    def text(self) -> str:
    @property
    def identifier(self) -> str:          # "source#chunk_id"
```

### `RAGResponse`

Returned by `NaiveRAG`, `AdvancedRAG`, and `AgenticRAG`.

```python
@dataclass
class RAGResponse:
    question: str                         # Original question
    answer: str                           # Generated answer
    context: str = ""                     # Formatted context used
    sources: list[dict] = []              # Source documents
    took_ms: int = 0                      # Total execution time
    confidence: float = 1.0               # Confidence score
    reasoning_summary: str = ""           # Human-readable pipeline summary
    agent_log: list[dict] = []            # Agent action log (AgenticRAG)
    llm_calls: int = 1                    # Number of LLM API calls made
```

### `AgentResponse`

Returned by `ReActAgent`.

```python
@dataclass
class AgentResponse:
    question: str
    answer: str
    sources: list[dict] = []
    retrieved_evidence: list[dict] = []   # All unique chunks retrieved
    trajectory: list[AgentStep] = []      # Reasoning steps
    reasoning_summary: str = ""
    confidence: float = 1.0
    total_steps: int = 0
    took_ms: int = 0
    llm_calls: int = 0
```

### `AgentStep`

```python
@dataclass
class AgentStep:
    step_num: int
    thought: str
    action: str                           # "search", "list_docs", "final_answer"
    action_input: dict = {}
    observation: str = ""
    chunks_retrieved: int = 0
    took_ms: int = 0
```

---

## 14. Exception Hierarchy

```
RAGException (base)
├── ConfigurationError     # Missing env vars, invalid config
├── IngestionError         # Document parsing/ingestion failure
├── RetrievalError         # Vector DB search/connection failure
└── LLMGenerationError     # LLM API call or response parsing failure
```

```python
from polyrag import RAGException, ConfigurationError, IngestionError, RetrievalError, LLMGenerationError

try:
    response = app.query("...")
except LLMGenerationError as e:
    print(f"LLM failed: {e}")
except RetrievalError as e:
    print(f"Vector search failed: {e}")
except RAGException as e:
    print(f"RAG error: {e}")
```

---

## 15. Known Issues & Gotchas

### 15.1 🐛 `persist_path` vs `persist_directory` Mismatch

`PolyRAG.create()`, `RAGService.create()`, and `RAGService.from_env()` pass `persist_path=` to `ChromaVectorStore`, but its constructor expects `persist_directory=`. This causes a `TypeError`.

**Workaround**: Create `ChromaVectorStore` manually:

```python
from polyrag import PolyRAG, ChromaVectorStore

store = ChromaVectorStore(persist_directory="./chroma_db", collection_name="kb")
app = PolyRAG(vector_store=store)
```

### 15.2 No Milvus Support (Yet)

PolyRAG only ships with `ChromaVectorStore` and `InMemoryVectorStore`. To use Milvus, you need to implement `BaseVectorStore` yourself (see [Section 11.3](#113-custom-vector-store-eg-milvus)).

### 15.3 OpenAI API Key Required for LLM

Even if you only want retrieval (no generation), `PolyRAG.create()` and `from_env()` instantiate `OpenAILLM` by default, which creates an OpenAI client. Set `OPENAI_API_KEY` in your environment or pass a custom LLM client.

### 15.4 Sentence Transformers Import

`SentenceTransformerEmbedding` imports `sentence-transformers` lazily. If not installed, you get a clear error. Install with:
```bash
pip install sentence-transformers
```

### 15.5 Chunker Defaults

Default chunker is `RecursiveCharacterChunker(chunk_size=550, chunk_overlap=35)`. For short KB articles (like support troubleshooting docs), consider increasing `chunk_size` or using the whole article as a single chunk.

---

## 16. Complete API Reference

### Top-Level Exports (`from polyrag import ...`)

| Export | Type | Description |
|--------|------|-------------|
| `PolyRAG` | class | Main application context + pipeline factory |
| `Container` | class | Dependency injection container |
| `RAGService` | class | High-level facade (extends PolyRAG) |
| `AgenticRAGService` | class | Agentic RAG facade |
| `BaseRAG` | ABC | Abstract base for all pipelines |
| `NaiveRAG` | class | Simple retrieve-then-read pipeline |
| `AdvancedRAG` | class | Multi-query + RRF fusion pipeline |
| `AgenticRAG` | class | Multi-round retrieval + reflection pipeline |
| `ReActAgent` / `ReActRAG` | class | Thought-Action-Observation agent |
| `BaseChunker` | ABC | Chunker interface |
| `FixedSizeChunker` | class | Fixed-size sliding window chunker |
| `RecursiveCharacterChunker` | class | Recursive separator-based chunker |
| `BaseEmbeddingModel` | ABC | Embedding interface |
| `SentenceTransformerEmbedding` | class | Local HuggingFace embeddings |
| `OpenAIEmbedding` | class | OpenAI API embeddings |
| `BaseVectorStore` | ABC | Vector store interface |
| `ChromaVectorStore` | class | ChromaDB persistent store |
| `InMemoryVectorStore` | class | In-memory cosine similarity store |
| `MilvusVectorStore` / `MilvusLiteVectorStore` | class | Milvus / Milvus Lite vector store (v0.1.5+) |
| `BaseLLMClient` | ABC | LLM client interface |
| `OpenAILLM` / `ChatOpenAI` | class | OpenAI / Azure / compatible LLM adapter |
| `resolve_chunker` | function | Auto-resolver for chunking strategy (v0.1.5+) |
| `resolve_embedding_model` | function | Auto-resolver for embedding models (v0.1.5+) |
| `resolve_llm_client` / `resolve_chat_model` | function | Auto-resolver for LLM clients (v0.1.5+) |
| `LangChainDocumentConverter` | class | Converter between LangChain Documents & PolyRAG (v0.1.5+) |
| `LangChainEmbeddingAdapter` | class | Adapter to wrap LangChain Embeddings (v0.1.5+) |
| `LangChainChatModelAdapter` | class | Adapter to wrap LangChain BaseChatModel (v0.1.5+) |
| `Document` | dataclass | Input document model |
| `Chunk` | dataclass | Chunked document segment |
| `SearchResult` | dataclass | Vector search result |
| `RAGResponse` | dataclass | Pipeline query response |
| `AgentAction` | dataclass | Agent action (thought + action) |
| `AgentStep` | dataclass | Agent reasoning step |
| `AgentResponse` | dataclass | ReAct agent response |
| `RAGException` | exception | Base exception |
| `ConfigurationError` | exception | Configuration error |
| `IngestionError` | exception | Ingestion error |
| `RetrievalError` | exception | Retrieval error |
| `LLMGenerationError` | exception | LLM generation error |

---

## End-to-End Example for ChatbotOCR Project

```python
"""
Complete example: Using PolyRAG for support chatbot knowledge retrieval.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from polyrag import (
    PolyRAG,
    ChromaVectorStore,
    SentenceTransformerEmbedding,
    OpenAILLM,
    RecursiveCharacterChunker,
)

# ── 1. Configure Components ──────────────────────────────
embedding = SentenceTransformerEmbedding(model_name="all-MiniLM-L6-v2")
vector_store = ChromaVectorStore(
    persist_directory="./data/chroma_db",
    collection_name="support_kb",
)
llm = OpenAILLM(model_name="gpt-4o-mini")
chunker = RecursiveCharacterChunker(chunk_size=800, chunk_overlap=50)

# ── 2. Create App ────────────────────────────────────────
app = PolyRAG(
    chunker=chunker,
    embedding_model=embedding,
    vector_store=vector_store,
    llm_client=llm,
)

# ── 3. Ingest Knowledge Base (run once) ──────────────────
kb_articles = [
    {
        "text": (
            "Error Code: AUTH-401 / HTTP 401\n"
            "Title: Invalid or expired authentication token\n"
            "Product: Customer Portal\n"
            "Problem: User receives an Unauthorized access error.\n"
            "Resolution:\n"
            "1. Verify the user's authentication status.\n"
            "2. Check token expiration.\n"
            "3. Refresh the session.\n"
            "4. Check the authentication service logs if the issue persists."
        ),
        "source": "kb-auth-001.md",
        "metadata": {"category": "authentication", "error_code": "AUTH-401", "article_id": "KB-AUTH-001"},
    },
    {
        "text": (
            "Error Code: DB-409 / HTTP 409 / SQLSTATE[23000]\n"
            "Title: Duplicate key violation\n"
            "Problem: Record creation fails due to unique constraint.\n"
            "Resolution:\n"
            "1. Check if the record already exists.\n"
            "2. Use upsert instead of insert.\n"
            "3. Review the unique constraint definition."
        ),
        "source": "kb-db-001.md",
        "metadata": {"category": "database", "error_code": "DB-409", "article_id": "KB-DB-001"},
    },
]

for article in kb_articles:
    app.ingest_text(
        text=article["text"],
        source=article["source"],
        metadata=article["metadata"],
    )

print(f"Ingested {vector_store.count()} chunks into vector store.")

# ── 4. Query with NaiveRAG ───────────────────────────────
response = app.query("AUTH-401 invalid token error", top_k=3)
print(f"\n🤖 Answer: {response.answer}")
print(f"📚 Sources: {response.sources}")
print(f"⏱ Took: {response.took_ms}ms")

# ── 5. Query with AdvancedRAG ────────────────────────────
advanced = app.create_advanced_rag(top_k=5, num_expanded_queries=3)
response = advanced.execute("How to fix duplicate key violation?")
print(f"\n🧠 Advanced Answer: {response.answer}")

# ── 6. Query with AgenticRAG ────────────────────────────
agentic = app.create_agentic_rag(top_k=3, max_rounds=2, verbose=True)
response = agentic.execute("Troubleshoot authentication error on portal")
print(f"\n🤖 Agentic Answer: {response.answer}")
print(f"📊 Confidence: {response.confidence}")
print(f"📝 Agent Log: {len(response.agent_log)} actions")
```
