"""Use case for Naive (Standard Retrieve-then-Read) RAG."""

import time
from typing import Any

from src.domain.entities.rag_response import RAGResponse
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.domain.interfaces.llm import LLMClientInterface
from src.domain.interfaces.vector_store import VectorStoreInterface


class NaiveRAGUseCase:
    """Standard retrieve-then-read RAG use case."""

    def __init__(
        self,
        embedding_model: EmbeddingModelInterface,
        vector_store: VectorStoreInterface,
        llm_client: LLMClientInterface | None = None,
    ) -> None:
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.llm_client = llm_client

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve top-k search results for a query string."""
        query_vector = self.embedding_model.embed_text(query)
        return self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
        )

    def format_context(
        self,
        search_results: list[dict[str, Any]],
    ) -> str:
        """Format search results into clean context blocks."""
        blocks: list[str] = []
        for result in search_results:
            document = result.get("document", {})
            source = document.get("source", "unknown")
            chunk_id = document.get("chunk_id", "")
            text = document.get("text", "")
            blocks.append(f"Source: {source}#{chunk_id}\n{text}")

        return "\n\n---\n\n".join(blocks)

    def execute(
        self,
        question: str,
        top_k: int = 5,
    ) -> RAGResponse:
        """Execute retrieve-then-read RAG pipeline."""
        start_time = time.time()

        results = self.retrieve(question, top_k=top_k)
        context = self.format_context(results)

        if not self.llm_client:
            took_ms = int((time.time() - start_time) * 1000)
            return RAGResponse(
                question=question,
                answer="",
                context=context,
                sources=[r.get("document", {}) for r in results],
                took_ms=took_ms,
                confidence=0.5,
                reasoning_summary="Retrieved evidence without LLM generation.",
                llm_calls=0,
            )

        prompt = (
            "Use the following context to answer the question. "
            "If the answer is not in the context, say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

        answer = self.llm_client.complete(prompt)
        took_ms = int((time.time() - start_time) * 1000)

        return RAGResponse(
            question=question,
            answer=answer,
            context=context,
            sources=[r.get("document", {}) for r in results],
            took_ms=took_ms,
            confidence=0.85,
            reasoning_summary=f"Retrieved {len(results)} chunks and generated answer using {self.llm_client.model_name}.",
            llm_calls=1,
        )

    def query(self, question: str, top_k: int = 5) -> dict[str, Any]:
        """Backward-compatible query dictionary method."""
        return self.execute(question, top_k=top_k).to_dict()
