# Agentic RAG System

## Project Overview

This project implements an Agentic Retrieval-Augmented Generation (RAG) system. Unlike a standard RAG pipeline where retrieval happens once before answer generation, the agent actively controls the retrieval process through query refinement, iterative retrieval, and self-evaluation.

The system should be built from scratch without relying on framework-provided RAG abstractions.

---

## Functional Requirements

### 1. Document Processing

The system must:

- Load documents from a local dataset.
- Perform custom text chunking.
- Generate embeddings for every chunk.
- Store embeddings inside a vector database.

### 2. Vector Store

The system must:

- Support semantic similarity search.
- Return top-k relevant chunks.
- Persist embeddings locally.

Example technologies:

- FAISS
- ChromaDB
- SQLite + vector extension

### 3. Embedding Pipeline

The system must:

- Create embeddings during indexing.
- Reuse stored embeddings during querying.
- Support rebuilding embeddings when documents change.

### 4. Agent-Controlled Retrieval

The agent must determine:

- Whether retrieval is necessary.
- What query should be sent to the retriever.
- Whether additional retrieval rounds are required.

Capabilities include:

- Query rewriting
- Retrieval planning
- Multi-round retrieval
- Context expansion

### 5. Multi-Hop Retrieval

The agent should support questions requiring evidence from multiple sources.

Example:

Question:
"Which company acquired GitHub and who was the CEO at the time?"

Expected behavior:

1. Retrieve information about GitHub acquisition.
2. Identify acquiring company.
3. Retrieve information about CEO during acquisition.
4. Combine evidence.
5. Generate answer.

### 6. Reflection and Self-Check

Before producing the final answer, the agent must:

- Evaluate retrieved evidence.
- Detect missing information.
- Trigger another retrieval round if needed.
- Verify confidence in the answer.

### 7. Answer Generation

The final response should contain:

- Answer
- Retrieved evidence
- Sources/chunks used
- Agent reasoning summary

---

## Non-Functional Requirements

### Performance

- Query response should complete within reasonable time.
- Retrieval latency should remain low for small datasets.

### Maintainability

- Clear separation between:
  - Chunking
  - Embedding
  - Retrieval
  - Agent logic
  - LLM generation

### Transparency

- Agent decisions should be logged.
- Retrieval rounds should be observable.

---

## Acceptance Criteria

### Evaluation Improvement

Create a benchmark consisting of 20 questions.

Compare:

1. Naive RAG
   - Single retrieval round
   - Direct answer generation

2. Agentic RAG
   - Query rewriting
   - Multi-round retrieval
   - Reflection

Success Criteria:

- Agentic RAG achieves at least 20% improvement over Naive RAG.

---

### Multi-Hop Demonstration

Provide at least one question that requires:

- Multiple retrieval rounds
- Information gathered from multiple chunks

The system logs should clearly show:

- Round 1 retrieval
- Query refinement
- Round 2 retrieval
- Final synthesis

---

### Reflection Report

Provide a written reflection (minimum 5 sentences) covering:

- When Agentic RAG performs better than standard RAG
- Benefits of query rewriting
- Benefits of iterative retrieval
- Limitations of the approach
- Potential future improvements

---

## Constraints

- Hand-written implementation.
- No one-line framework solutions.
- Core retrieval pipeline must be implemented manually.
``