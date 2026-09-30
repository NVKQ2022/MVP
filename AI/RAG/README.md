# Agentic RAG (Option B)

A hand-rolled Retrieval-Augmented Generation (RAG) system where retrieval is driven dynamically by an autonomous agent loop featuring **query rewriting**, **multi-round iterative retrieval**, and **self-reflective verification** before synthesizing the final grounded answer.

Built completely from scratch without monolithic orchestration frameworks (no LangChain, no LlamaIndex one-liners).

---

## Table of Contents
- [Overview & Screenshot Requirements](#overview--screenshot-requirements)
- [Key Features](#key-features)
  - [1. Hand-Rolled Core Components](#1-hand-rolled-core-components)
  - [2. Autonomous Agent Loop](#2-autonomous-agent-loop)
- [Acceptance Criteria Verification](#acceptance-criteria-verification)
  - [1. 20-Question Evaluation (≥ +20% Improvement)](#1-20-question-evaluation---20-improvement)
  - [2. Multi-Hop Question Requiring ≥ 2 Retrieval Rounds](#2-multi-hop-question-requiring--2-retrieval-rounds)
  - [3. Reflection: When Does Agentic RAG Win?](#3-reflection-when-does-agentic-rag-win)
- [Project Architecture & Directory Layout](#project-architecture--directory-layout)
- [Setup & Installation](#setup--installation)
- [How to Run](#how-to-run)
  - [Run Agentic RAG with Observable Trajectory](#run-agentic-rag-with-observable-trajectory)
  - [Run 20-Question Benchmark](#run-20-question-benchmark)
  - [Inspect Chroma Vector Store](#inspect-chroma-vector-store)
  - [Run Web Server & Frontend](#run-web-server--frontend)

---

## Overview & Screenshot Requirements

| Requirement | Specification | Implementation Status |
|---|---|---|
| **Hand-rolled chunking** | Custom text chunking algorithm with configurable overlap | ✅ `chunking.py` (`FixedSizeChunkingService`) |
| **Hand-rolled embedding** | Normalized vector embedding service (OpenAI & HF Sentence-Transformers) | ✅ `embedding.py` (`EmbeddingService`) |
| **Vector store** | Hand-crafted ChromaDB vector store interface & cosine search | ✅ `vectordb.py` (`ChromaVectorDB`) |
| **Agent decision loop** | Agent dynamically decides when, what, and how many rounds to retrieve | ✅ `agenticRag.py` (`AgenticRAGService`) |
| **Query rewrite** | Expands conversational input into protocol-dense technical queries | ✅ `AgenticRAGService.decide_retrieval` |
| **Multi-round retrieval** | Iterative retrieval with chunk deduplication across multiple RFCs | ✅ `AgenticRAGService.query` |
| **Self-check reflection** | Verifies sufficiency, detects information gaps, checks citations | ✅ `AgenticRAGService.reflect_and_evaluate` |
| **20-Question Eval** | Target: ≥ +20% over naive retrieve-then-read | ✅ **+23.06% Relative Improvement** |
| **Multi-hop Question** | Must trigger ≥ 2 retrieval rounds | ✅ Verified (DNS UDP truncation & TCP fallback) |
| **5+ Sentence Reflection** | English reflection detailing when Agentic RAG outperforms Naive RAG | ✅ Included in `docs/reflection.md` & below |

---

## Key Features

### 1. Hand-Rolled Core Components
- **Chunking (`chunking.py`)**: Hand-rolled sliding window character chunker with customizable step size, overlap boundaries, and empty chunk dropping.
- **Embedding (`embedding.py`)**: Dual-provider embedding abstraction supporting cloud embeddings (`text-embedding-3-small`, `text-embedding-3-large`) and local Sentence-Transformers (`all-MiniLM-L6-v2`) with batching and normalization.
- **Vector Database (`vectordb.py`)**: Direct ChromaDB persistent client wrapper computing cosine distance, metadata tagging (`source`, `chunk_id`), batch indexing, and collection inspection.

### 2. Autonomous Agent Loop
Instead of standard naive retrieve-then-read (which issues a single query and blindly answers), the agent loop executes four explicit phases:

```
[User Question]
       │
       ▼
[1. Planning & Query Rewrite] ── (Retrieval Not Needed) ──► [Direct Answer]
       │ (Retrieval Needed)
       ▼
[2. Vector Search (Round 1)]
       │
       ▼
[3. Chunk Deduplication & Context Assembly]
       │
       ▼
[4. Fused Reflection & Sufficiency Self-Check]
       ├── (Sufficient) ──────────────────────────────────► [Synthesize Grounded Answer with Citations]
       └── (Gaps Detected & Rounds Remaining)
               │
               ▼
       [Query Refinement & Expansion]
               │
               ▼
       [Vector Search (Round 2+)] ──► [Loop to Step 3]
```

1. **Planning & Query Rewriting**: Classifies whether retrieval is necessary (bypassing conversational/greeting queries) and reformulates conversational questions into keyword-dense RFC queries.
2. **Iterative Multi-Round Retrieval**: Queries the vector index, deduplicating newly acquired chunks against previously seen chunks to prevent context pollution.
3. **Fused Reflection & Self-Check**: Evaluates accumulated evidence for factual completeness. If facts are missing, it isolates the knowledge gap and synthesizes an improved search query for the next round.
4. **Grounded Answer Synthesis**: Generates final answers strictly grounded in the retrieved chunks with precise inline citations in the format `[<source_file>#<chunk_id>]`.

---

## Acceptance Criteria Verification

### 1. 20-Question Evaluation (≥ +20% Improvement)

The system was benchmarked across **20 questions** covering single-hop, multi-hop, and cross-RFC comparative domains against 8 networking RFC documents (`RFC 791`, `RFC 793`, `RFC 1035`, `RFC 6749`, `RFC 8259`, `RFC 8446`, `RFC 9000`, `RFC 9110`):

| Question ID | Category | Question Summary | Naive RAG Score | Agentic RAG Score | Improvement |
|:---:|:---:|:---|:---:|:---:|:---:|
| 1 | Single-hop | DNS Primary Purpose (RFC 1035) | 60.0% | **80.0%** | **+20.0%** |
| 2 | Single-hop | OAuth 2.0 Grant Types (RFC 6749) | 100.0% | 100.0% | +0.0% |
| 3 | Single-hop | IPv4 Min/Max Header Size (RFC 791) | 80.0% | 80.0% | +0.0% |
| 4 | Single-hop | TCP 3-Way Handshake Flags (RFC 793) | 100.0% | 100.0% | +0.0% |
| 5 | Single-hop | JSON Primitive Data Types (RFC 8259) | 66.7% | 66.7% | +0.0% |
| 6 | Single-hop | TLS 1.3 Latency Improvement (RFC 8446) | 75.0% | 50.0% | -25.0% |
| 7 | Single-hop | QUIC Transport Layer Base (RFC 9000) | 66.7% | 66.7% | +0.0% |
| 8 | Single-hop | HTTP 429 Status Semantics (RFC 9110) | 33.3% | **100.0%** | **+66.7%** |
| 9 | Multi-hop | HTTP/3 Transport Protocol & RFC | 75.0% | **100.0%** | **+25.0%** |
| 10 | Multi-hop | DNS UDP Truncation (1035) & TCP Flags (793) | 66.7% | **83.3%** | **+16.7%** |
| 11 | Multi-hop | OAuth Token Exchange Security & TLS 1.3 | 66.7% | 50.0% | -16.7% |
| 12 | Multi-hop | TCP Termination (793) vs IPv4 Fragmentation (791) | 60.0% | **80.0%** | **+20.0%** |
| 13 | Multi-hop | QUIC Stream Multiplexing vs HTTP/2 over TCP | 20.0% | **100.0%** | **+80.0%** |
| 14 | Multi-hop | TLS 1.3 0-RTT Replay & HTTP Safe Methods | 75.0% | 75.0% | +0.0% |
| 15 | Multi-hop | IPv4 TTL Loop Prevention & TCP Retransmit | 20.0% | **40.0%** | **+20.0%** |
| 16 | Multi-hop | DNS MX Record Resolution & Port Standards | 20.0% | **80.0%** | **+60.0%** |
| 17 | Comparative | TCP 3-Way Handshake vs QUIC 0/1-RTT | 75.0% | 75.0% | +0.0% |
| 18 | Comparative | OAuth Bearer Tokens vs HTTP Auth Headers | 83.3% | 83.3% | +0.0% |
| 19 | Comparative | JSON UTF-8 vs DNS Domain Label Encodings | 60.0% | **80.0%** | **+20.0%** |
| 20 | Comparative | TLS 1.3 Security Guarantees vs Raw TCP/IP | 40.0% | 40.0% | +0.0% |

#### Benchmark Summary
- **Average Naive RAG Score**: `62.17%`
- **Average Agentic RAG Score**: `76.50%`
- **Relative Improvement**: **`+23.06%`** *(Exceeds acceptance threshold of ≥ +20%)*

---

### 2. Multi-Hop Question Requiring ≥ 2 Retrieval Rounds

#### Test Question
> *"When a DNS response exceeds the UDP size limit in RFC 1035, which header bit is set, and what TCP flags defined in RFC 793 are sent to initiate the fallback connection?"*

#### Agent Execution Trajectory

```text
>> [ACTION: PLANNING]
   • retrieval_needed: True
   • query: RFC 1035 DNS UDP size limit header bit truncation RFC 793 TCP flags fallback

--- [ROUND 1 OF 3] ---
>> [ACTION: VECTOR_SEARCH]
   • round: 1
   • retrieved_count: 3 chunks
>> [ACTION: DEDUPLICATION]
   • new_chunks_added: 3 (rfc1035.txt#140, rfc1035.txt#141, rfc1035.txt#142)
>> [ACTION: REFLECTION_AND_EVALUATION]
   • is_sufficient: False
   • reason: Identified TC (Truncation) bit from RFC 1035, but missing TCP handshake flags from RFC 793.
   • missing_gaps: ['RFC 793 TCP connection initiation control flags']
   • next_query: RFC 793 TCP connection initiation control flags SYN ACK three-way handshake

--- [ROUND 2 OF 3] ---
>> [ACTION: VECTOR_SEARCH]
   • round: 2
   • query: RFC 793 TCP connection initiation control flags SYN ACK three-way handshake
   • retrieved_count: 3 chunks
>> [ACTION: DEDUPLICATION]
   • new_chunks_added: 3 (rfc793.txt#88, rfc793.txt#89, rfc793.txt#90)
>> [ACTION: REFLECTION_AND_EVALUATION]
   • is_sufficient: True
   • reason: Evidence contains both TC bit from RFC 1035 and SYN control flag from RFC 793.
   • decision: Evidence sufficient! Answer synthesized directly with citations.
```

#### Final Answer
> *"When a DNS response exceeds the 512-byte UDP limit in RFC 1035, the **TC (Truncation) bit** in the header is set to 1, indicating that the message was truncated [rfc1035.txt#140]. To initiate the fallback connection over TCP, the client transmits a TCP packet with the **SYN (Synchronize) control flag** set to establish the connection via the three-way handshake defined in RFC 793 [rfc793.txt#88]."*

---

### 3. Reflection: When Does Agentic RAG Win?

*(5+ sentence reflection on system performance from `docs/reflection.md`)*

> Agentic RAG significantly outperforms standard retrieve-then-read RAG when queries require multi-hop reasoning, intermediate entity resolution, or cross-document synthesis across disparate technical specifications. Standard RAG relies on a single retrieval round; if the initial semantic search fails to capture all relevant facets of a question or returns incomplete context, naive RAG inevitably hallucinates or produces a truncated answer. In contrast, Agentic RAG actively plans its retrieval, evaluates the completeness of the retrieved evidence against the user's objective, and iteratively detects knowledge gaps. When missing details or secondary protocol references are identified, the agent formulates a refined, targeted search query to pull supplementary evidence before synthesizing a final grounded answer. Furthermore, by performing query rewriting, the agent bridges the vocabulary gap between conversational user prompts and dense domain terminology (such as expanding protocol acronyms into specific RFC numbers and control flags). Consequently, while standard RAG is suitable for simple, single-chunk lookups, Agentic RAG is essential whenever answering requires investigative exploration, verification, and multi-source evidence combination.

---

## Project Architecture & Directory Layout

```text
AI/RAG/
├── agenticRag.py             # Agentic RAG Engine (Planning, Multi-Round Loop, Fused Reflection)
├── rag_service.py            # Naive Retrieve-then-Read RAG Service
├── chunking.py               # Hand-rolled character chunking with sliding window & overlap
├── embedding.py              # Embedding abstractions (OpenAI & Sentence-Transformers)
├── vectordb.py               # ChromaDB vector store adapter & cosine search
├── config.py                 # Configuration & environment variable loader
├── main.py                   # Dependency wiring and factory initializers
├── startAgenticRag.py        # CLI executable for running Agentic RAG queries
├── benchmark.py              # 20-Question benchmark evaluation script
├── scripts/                  # Management scripts
│   ├── build_chunks.py       # Chunk generation pipeline from data/docs/
│   ├── build_embeddings.py   # Embedding computation and vector indexer
│   ├── info_chroma.py        # Chroma collection statistics & inspector
│   ├── clean_chroma.py       # Store cleaner for reproducibility
│   ├── query.py              # Direct vector search CLI
│   ├── rag_query.py          # Naive RAG CLI
│   └── server.py             # FastAPI server with UI & REST endpoints
├── data/
│   ├── docs/                 # Raw RFC specifications (.txt)
│   └── chunks/               # Pre-chunked documents (.json)
├── docs/                     # Specifications, requirements, benchmarks & reflection
│   ├── benchmarkResult.md    # 20-question evaluation report
│   ├── reflection.md         # Reflection report on Agentic RAG performance
│   ├── requirementUpdate.md  # Project requirements and acceptance criteria
│   └── how-to-use.md         # Extended developer guide
└── tests/                    # Test suite
    └── test_info_chroma.py   # Chroma inspector unit test
```

---

## Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Virtual environment (`venv` or `conda`)

### 2. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
ENDPOINT="https://your-llm-endpoint.openai.azure.com"
API_KEY="your-api-key"
MODEL_NAME="gpt-4o-mini"
PROVIDER="openai"
EMBEDDING_MODEL="text-embedding-3-small"
CHROMA_PERSIST_DIR="chroma_db"
CHROMA_COLLECTION="rfc_docs"
```

---

## How to Run

### Run Agentic RAG with Observable Trajectory
Execute an end-to-end multi-hop query with full action logging:
```bash
python startAgenticRag.py --query "When a DNS response exceeds the UDP size limit in RFC 1035, which header bit is set, and what TCP flags defined in RFC 793 are sent to initiate the fallback connection?"
```

Custom options:
```bash
python startAgenticRag.py --top-k 3 --max-rounds 3 --query "Your question here"
```

### Run 20-Question Benchmark
Evaluate Naive RAG vs Agentic RAG across the RFC dataset:
```bash
python benchmark.py
```

### Inspect Chroma Vector Store
View total indexed chunks, dimension, distance metrics, and per-document counts:
```bash
python scripts/info_chroma.py
```

To output raw JSON:
```bash
python scripts/info_chroma.py --json
```

### Run Web Server & Frontend
Launch the FastAPI server:
```bash
python scripts/server.py --port 8000
```
- Web UI: `http://localhost:8000/`
- Interactive API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`