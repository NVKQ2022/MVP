# Agentic RAG

A standard RAG where retrieval is driven by the agent: query rewrite, multi-round retrieval, and a self-check before the final answer.

## Must Include
- Hand-rolled chunking + embedding + vector store
- Agent loop decides when and what to retrieve

## Acceptance
- 20-question eval: ≥ +20% over naive retrieve-then-read
- Multi-hop question needing ≥2 retrieval rounds
- 5+ sentence English reflection: when does agentic win

**Estimated effort:** ≈ 4–5 h · hand-written, no framework one-liners