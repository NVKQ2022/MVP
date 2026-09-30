"""Composition Root / Dependency Injection Container.

Wires domain interfaces to infrastructure adapters and application use cases.
"""

from typing import Any

from src.application.use_cases.agentic_rag import AgenticRAGUseCase
from src.application.use_cases.evaluate_benchmark import EvaluateBenchmarkUseCase
from src.application.use_cases.ingest_documents import IngestDocumentsUseCase
from src.application.use_cases.naive_rag import NaiveRAGUseCase
from src.application.use_cases.react_agent import ReActAgentUseCase
from src.domain.interfaces.chunker import ChunkerInterface
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.domain.interfaces.llm import LLMClientInterface
from src.domain.interfaces.vector_store import VectorStoreInterface
from src.infrastructure.chunking.fixed_size import FixedSizeChunker
from src.infrastructure.config.settings import Settings, settings
from src.infrastructure.embedding.openai_embedding import OpenAIEmbeddingAdapter
from src.infrastructure.embedding.sentence_transformer import SentenceTransformerEmbeddingAdapter
from src.infrastructure.llm.openai_adapter import OpenAILLMAdapter
from src.infrastructure.vector_store.chroma_adapter import ChromaVectorStoreAdapter


class Container:
    """Factory container for building application components."""

    def __init__(self, app_settings: Settings | None = None) -> None:
        self.settings = app_settings or settings

    def build_chunker(
        self,
        chunk_size: int = 550,
        overlap: int = 35,
        drop_empty: bool = True,
    ) -> ChunkerInterface:
        """Build document chunker."""
        return FixedSizeChunker(
            chunk_size=chunk_size,
            overlap=overlap,
            drop_empty=drop_empty,
        )

    def build_embedding_model(
        self,
        provider: str | None = None,
        model_name: str | None = None,
    ) -> EmbeddingModelInterface:
        """Build embedding adapter based on configuration."""
        active_provider = provider or self.settings.provider
        active_model = model_name or self.settings.embedding_model

        if active_provider == "openai":
            return OpenAIEmbeddingAdapter(
                model_name=active_model,
                base_url=self.settings.endpoint or None,
                api_key=self.settings.api_key or None,
            )

        if active_provider in ("hf", "sentence_transformers"):
            return SentenceTransformerEmbeddingAdapter(
                model_name=active_model or "all-MiniLM-L6-v2",
            )

        raise ValueError(f"Unsupported embedding provider: {active_provider}")

    def build_vector_store(
        self,
        persist_dir: str | None = None,
        collection_name: str | None = None,
    ) -> VectorStoreInterface:
        """Build ChromaDB vector store adapter."""
        return ChromaVectorStoreAdapter(
            persist_directory=persist_dir or self.settings.chroma_persist_dir,
            collection_name=collection_name or self.settings.chroma_collection,
        )

    def build_llm_client(
        self,
        model_name: str | None = None,
        endpoint: str | None = None,
        api_key: str | None = None,
    ) -> LLMClientInterface:
        """Build LLM client adapter."""
        return OpenAILLMAdapter(
            model_name=model_name or self.settings.model_name,
            base_url=endpoint or self.settings.endpoint or None,
            api_key=api_key or self.settings.api_key or None,
        )

    def build_naive_rag(
        self,
        embedding_model: EmbeddingModelInterface | None = None,
        vector_store: VectorStoreInterface | None = None,
        llm_client: LLMClientInterface | None = None,
    ) -> NaiveRAGUseCase:
        """Build Naive RAG use case."""
        embedder = embedding_model or self.build_embedding_model()
        store = vector_store or self.build_vector_store()
        llm = llm_client
        if llm is None and self.settings.api_key and self.settings.endpoint:
            llm = self.build_llm_client()

        return NaiveRAGUseCase(
            embedding_model=embedder,
            vector_store=store,
            llm_client=llm,
        )

    def build_agentic_rag(
        self,
        naive_rag: NaiveRAGUseCase | None = None,
        llm_client: LLMClientInterface | None = None,
        top_k: int = 3,
        max_rounds: int = 3,
        verbose: bool = True,
    ) -> AgenticRAGUseCase:
        """Build Agentic RAG use case."""
        naive = naive_rag or self.build_naive_rag()
        llm = llm_client or self.build_llm_client()

        return AgenticRAGUseCase(
            naive_rag=naive,
            llm_client=llm,
            top_k=top_k,
            max_rounds=max_rounds,
            verbose=verbose,
        )

    def build_react_agent(
        self,
        llm_client: LLMClientInterface | None = None,
        embedding_model: EmbeddingModelInterface | None = None,
        vector_store: VectorStoreInterface | None = None,
        max_steps: int = 4,
        default_top_k: int = 3,
    ) -> ReActAgentUseCase:
        """Build ReAct agent use case."""
        return ReActAgentUseCase(
            llm_client=llm_client or self.build_llm_client(),
            embedding_model=embedding_model or self.build_embedding_model(),
            vector_store=vector_store or self.build_vector_store(),
            max_steps=max_steps,
            default_top_k=default_top_k,
        )

    def build_ingest_use_case(
        self,
        chunker: ChunkerInterface | None = None,
        embedding_model: EmbeddingModelInterface | None = None,
        vector_store: VectorStoreInterface | None = None,
    ) -> IngestDocumentsUseCase:
        """Build IngestDocuments use case."""
        return IngestDocumentsUseCase(
            chunker=chunker or self.build_chunker(),
            embedding_model=embedding_model or self.build_embedding_model(),
            vector_store=vector_store or self.build_vector_store(),
        )

    def build_benchmark_use_case(
        self,
        naive_rag: NaiveRAGUseCase | None = None,
        agentic_rag: AgenticRAGUseCase | None = None,
    ) -> EvaluateBenchmarkUseCase:
        """Build EvaluateBenchmark use case."""
        return EvaluateBenchmarkUseCase(
            naive_rag=naive_rag or self.build_naive_rag(),
            agentic_rag=agentic_rag or self.build_agentic_rag(verbose=False),
        )


# Global default container instance
default_container = Container()
