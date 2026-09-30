"""RAG Service implementation.

Delegates to Clean Architecture application use cases while preserving full backward compatibility.
"""

from typing import Any

from src.application.use_cases.ingest_documents import IngestDocumentsUseCase
from src.application.use_cases.naive_rag import NaiveRAGUseCase
from src.domain.interfaces.chunker import ChunkerInterface
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.domain.interfaces.llm import LLMClientInterface
from src.domain.interfaces.vector_store import VectorStoreInterface
from src.infrastructure.config.settings import MODEL_NAME
from src.infrastructure.llm.openai_adapter import OpenAILLMAdapter


class RAGService:
    """RAG service for document ingestion, retrieval, and generation."""

    def __init__(
        self,
        client: Any,
        chunking_service: ChunkerInterface,
        embedding_service: EmbeddingModelInterface,
        vector_db: VectorStoreInterface,
        model_name: str = MODEL_NAME,
    ) -> None:
        self.client = client
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.vector_db = vector_db
        self.model_name = model_name

        # Adapt client to LLMClientInterface if needed
        if client is not None and not isinstance(client, LLMClientInterface):
            self.llm_client = OpenAILLMAdapter(
                model_name=model_name,
                client=client,
            )
        else:
            self.llm_client = client

        self.ingest_use_case = IngestDocumentsUseCase(
            chunker=chunking_service,
            embedding_model=embedding_service,
            vector_store=vector_db,
        )

        self.naive_rag = NaiveRAGUseCase(
            embedding_model=embedding_service,
            vector_store=vector_db,
            llm_client=self.llm_client,
        )

    def ingest(
        self,
        text: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Chunk, embed, and store a document in the vector database."""
        return self.ingest_use_case.ingest_text(
            text=text,
            source=source,
            metadata=metadata,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Find the top-k most relevant chunks for a query."""
        return self.naive_rag.retrieve(query=query, top_k=top_k)

    def format_context(
        self,
        search_results: list[dict[str, Any]],
    ) -> str:
        """Format search results into a clean context string."""
        return self.naive_rag.format_context(search_results)

    def query(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Perform end-to-end RAG: retrieve context and generate an answer."""
        response = self.naive_rag.execute(question=question, top_k=top_k)
        return {
            "question": response.question,
            "answer": response.answer,
            "context": response.context,
            "sources": response.sources,
        }


__all__ = ["RAGService"]
