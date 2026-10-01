# Reflection Report: Agentic RAG vs Standard RAG

## 1. When Agentic RAG Performs Better Than Standard RAG
Agentic RAG delivers superior performance over standard (naive) RAG primarily when handling multi-hop reasoning, cross-document inquiries, and questions requiring intermediate entity resolution. In standard RAG, the system relies on a single retrieval step; if the initial semantic search fails to capture all necessary context or if the query involves distributed facts across multiple RFC documents, naive RAG produces incomplete or hallucinated answers. Agentic RAG continuously reasons about its current state of knowledge, identifying when facts are missing and taking proactive tool actions to retrieve supplementary evidence.

## 2. Benefits of Query Rewriting
Query rewriting bridges the terminology gap between user prompts and dense technical specifications. By rewriting questions, the agent expands protocol acronyms (e.g. expanding "DNS message limits" to "RFC 1035 UDP 512 truncation TCP"), extracts exact RFC identifiers, and isolates key technical tokens. This substantially improves vector search precision and ensures candidate chunks returned from ChromaDB contain the exact technical definitions needed.

## 3. Benefits of Iterative Retrieval
Iterative retrieval enables the ReAct agent to conduct multi-stage investigative reasoning. In a multi-hop scenario (such as finding what transport protocol HTTP/3 uses and how its connection migration works), the agent retrieves the first fact in Step 1 (identifying QUIC in RFC 9000), observes the result, and subsequently issues a refined query in Step 2 specifically targeting QUIC connection migration and Connection IDs. This iterative feedback loop mimics human analytical problem-solving.

## 4. Limitations of the Approach
The primary trade-offs of Agentic RAG are increased response latency and higher LLM token consumption due to the sequential Thought-Action-Observation loop. Additionally, if the vector database does not contain the required domain documents, the agent may exhaust its maximum step budget attempting to find non-existent information before concluding with a fallback answer.

## 5. Potential Future Improvements
Key potential enhancements include:
1. **Hybrid Retrieval**: Combining BM25 keyword matching with dense vector similarity search to improve exact technical token recall.
2. **Cross-Encoder Reranking**: Re-ranking candidate chunks before presenting them to the LLM to maximize context density.
3. **Parallel Sub-Query Execution**: Firing independent sub-queries in parallel for complex multi-part questions to reduce total latency.
4. **Trajectory Caching**: Persisting common multi-hop retrieval paths to allow instant responses for recurrent technical queries.
