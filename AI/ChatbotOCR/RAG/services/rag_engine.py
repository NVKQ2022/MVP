"""PolyRAG Engine: Integrates polyrag 0.1.5 NaiveRAG to ingest and retrieve support KB documents."""

import logging
from pathlib import Path
from typing import Any

from polyrag import (
    NaiveRAG,
    RecursiveCharacterChunker,
    SentenceTransformerEmbedding,
    ChromaVectorStore,
    InMemoryVectorStore,
    OpenAILLM,
    RAGResponse,
)
from polyrag.core.interfaces import BaseVectorStore, BaseLLMClient

from RAG.config import rag_settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG Engine powered by PolyRAG 0.1.5 NaiveRAG pipeline.
    
    Coordinates:
    - Text document ingestion from data/kb_documents/
    - ChromaDB persistent storage / InMemory fallback
    - Semantic dense embedding search (SentenceTransformers / OpenAI)
    - Grounded 1-shot support answer generation using NaiveRAG
    """

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str | None = None,
        embedding_model: str | None = None,
        model_name: str | None = None,
        use_in_memory: bool = False,
    ) -> None:
        self.persist_dir = persist_dir or rag_settings.chroma_persist_dir
        self.collection_name = collection_name or rag_settings.chroma_collection_name
        self.embedding_model_name = embedding_model or rag_settings.embedding_model
        self.model_name = model_name or rag_settings.model_name

        # 1. Initialize Chunker
        self.chunker = RecursiveCharacterChunker(
            chunk_size=rag_settings.chunk_size,
            chunk_overlap=rag_settings.chunk_overlap,
        )

        # 2. Initialize Embeddings (OpenAI or Local Sentence Transformers)
        if self.embedding_model_name.startswith("text-embedding") and rag_settings.openai_api_key:
            from polyrag import OpenAIEmbedding
            logger.info(f"Initializing OpenAIEmbedding with model: {self.embedding_model_name}")
            self.embedding_model = OpenAIEmbedding(
                model_name=self.embedding_model_name,
                base_url=rag_settings.openai_base_url,
                api_key=rag_settings.openai_api_key,
            )
        else:
            logger.info(f"Initializing SentenceTransformerEmbedding with model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformerEmbedding(model_name=self.embedding_model_name)

        # 3. Initialize Vector Store (ChromaDB or InMemory)
        if use_in_memory:
            logger.info("Using InMemoryVectorStore")
            self.vector_store: BaseVectorStore = InMemoryVectorStore()
        else:
            logger.info(f"Initializing ChromaVectorStore (dir={self.persist_dir}, collection={self.collection_name})")
            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
            self.vector_store = ChromaVectorStore(
                persist_directory=self.persist_dir,
                collection_name=self.collection_name,
            )

        # 4. Initialize LLM Client
        self.llm_client: BaseLLMClient | None = None
        if rag_settings.openai_api_key:
            logger.info(f"Initializing OpenAILLM with model: {self.model_name}")
            self.llm_client = OpenAILLM(
                model_name=self.model_name,
                base_url=rag_settings.openai_base_url,
                api_key=rag_settings.openai_api_key,
            )
        else:
            logger.warning("No OPENAI_API_KEY found. RAG generation will run in retrieval-only mode.")

        # 5. Initialize NaiveRAG Pipeline (PolyRAG 0.1.5)
        self.naive_rag = NaiveRAG(
            chunker=self.chunker,
            embedding_model=self.embedding_model,
            vector_store=self.vector_store,
            llm_client=self.llm_client,
        )

    def ingest_kb_documents(
        self,
        docs_dir: str | Path | None = None,
        force_regenerate: bool = False,
    ) -> int:
        """
        Ingest all support text/markdown documents from the KB documents directory into PolyRAG NaiveRAG.
        Scans *.txt and *.md files directly as the primary knowledge base.
        """
        target_dir = Path(docs_dir or rag_settings.kb_docs_dir)

        if not target_dir.exists():
            raise FileNotFoundError(f"Knowledge base documents directory not found: {target_dir}")

        txt_files = sorted(list(target_dir.glob("*.txt")) + list(target_dir.glob("*.md")))
        if not txt_files:
            raise FileNotFoundError(f"No .txt or .md knowledge documents found in {target_dir}")

        logger.info(f"Found {len(txt_files)} knowledge base documents in {target_dir}. Ingesting into NaiveRAG vector store...")

        total_chunks = 0
        for f in txt_files:
            text = f.read_text(encoding="utf-8")
            # Parse header metadata if available
            metadata: dict[str, Any] = {"filename": f.name}
            for line in text.split("\n")[:6]:
                if ":" in line:
                    key, val = line.split(":", 1)
                    metadata[key.strip().lower().replace(" ", "_")] = val.strip()

            chunks = self.naive_rag.ingest_text(
                text=text,
                source=f.name,
                metadata=metadata,
            )
            total_chunks += len(chunks)

        logger.info(f"Ingested {total_chunks} chunks from {len(txt_files)} files. Total store count: {self.vector_store.count()}")
        return total_chunks

    def search(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        """Perform semantic vector search over the ingested knowledge base."""
        k = top_k or rag_settings.top_k
        return self.naive_rag.retrieve(query=query, top_k=k)

    def query_naive(self, question: str, top_k: int | None = None) -> RAGResponse:
        """Run standard Naive retrieve-then-read RAG pipeline using PolyRAG 0.1.5 NaiveRAG."""
        k = top_k or rag_settings.top_k
        return self.naive_rag.execute(question=question, top_k=k)

    # Convenience alias for primary query method
    query = query_naive

    def query_advanced(
        self,
        question: str,
        top_k: int | None = None,
        num_expanded_queries: int = 3,
        verbose: bool = False,
    ) -> RAGResponse:
        """Fallback to NaiveRAG when advanced pipeline is requested."""
        return self.query_naive(question=question, top_k=top_k)

    def query_agentic(
        self,
        question: str,
        top_k: int | None = None,
        max_rounds: int = 2,
        verbose: bool = False,
    ) -> RAGResponse:
        """Fallback to NaiveRAG when agentic pipeline is requested."""
        return self.query_naive(question=question, top_k=top_k)
