"""PolyRAG Engine: Integrates polyrag 0.2.0 NaiveRAG with Milvus Lite vector store."""

import logging
from pathlib import Path
from typing import Any

from polyrag import (
    NaiveRAG,
    RecursiveCharacterChunker,
    InMemoryVectorStore,
    RAGResponse,
)
from polyrag.embeddings import resolve_embedding_model
from polyrag.llms import resolve_llm_client
from polyrag.vector_stores import resolve_vector_store
from langchain_milvus import Milvus

from RAG.config import rag_settings

logger = logging.getLogger(__name__)


class MilvusLiteVectorStore(Milvus):
    """LangChain Milvus vector store tailored for Milvus Lite in PolyRAG."""

    def count(self) -> int:
        """Return total indexed records in the active collection."""
        try:
            if hasattr(self, "client") and self.client and hasattr(self, "collection_name"):
                if self.client.has_collection(collection_name=self.collection_name):
                    stats = self.client.get_collection_stats(collection_name=self.collection_name)
                    return int(stats.get("row_count", 0))
        except Exception:
            pass
        return 0

    def clear(self) -> None:
        """Drop collection to cleanly reset vector storage."""
        try:
            if hasattr(self, "client") and self.client and hasattr(self, "collection_name"):
                if self.client.has_collection(collection_name=self.collection_name):
                    self.client.drop_collection(collection_name=self.collection_name)
                    if hasattr(self, "col"):
                        self.col = None
                    if hasattr(self, "fields"):
                        self.fields = []
        except Exception:
            pass

    def peek(self, limit: int = 5) -> list[dict[str, Any]]:
        """Preview sample records from the vector collection."""
        try:
            if hasattr(self, "client") and self.client and hasattr(self, "collection_name"):
                if self.client.has_collection(collection_name=self.collection_name):
                    return self.client.query(
                        collection_name=self.collection_name,
                        filter="",
                        limit=limit,
                    )
        except Exception:
            pass
        return []


class RAGEngine:
    """
    RAG Engine powered by PolyRAG 0.2.0 NaiveRAG pipeline.
    
    Coordinates:
    - Text document ingestion from data/kb_documents/
    - Milvus Lite embedded vector store (with ChromaDB & InMemory fallback)
    - Semantic dense embedding search (HuggingFace / OpenAI via LangChain)
    - Grounded 1-shot support answer generation using NaiveRAG
    """

    def __init__(
        self,
        db_path: str | None = None,
        persist_dir: str | None = None,
        collection_name: str | None = None,
        embedding_model: str | None = None,
        model_name: str | None = None,
        use_in_memory: bool = False,
        vector_store_type: str | None = None,
    ) -> None:
        self.vector_store_type = (vector_store_type or rag_settings.vector_store_type).lower()
        self.collection_name = collection_name or (
            rag_settings.chroma_collection_name
            if self.vector_store_type in ("chroma", "chromadb")
            else rag_settings.milvus_collection_name
        )
        self.db_path = db_path or persist_dir or (
            rag_settings.chroma_persist_dir
            if self.vector_store_type in ("chroma", "chromadb")
            else rag_settings.milvus_db_path
        )
        self.persist_dir = self.db_path  # backward-compatible attribute
        self.embedding_model_name = embedding_model or rag_settings.embedding_model
        self.model_name = model_name or rag_settings.model_name

        # 1. Initialize Chunker
        self.chunker = RecursiveCharacterChunker(
            chunk_size=rag_settings.chunk_size,
            chunk_overlap=rag_settings.chunk_overlap,
        )

        # 2. Initialize Embeddings via PolyRAG 0.2.0 resolver
        if self.embedding_model_name.startswith("text-embedding") and rag_settings.openai_api_key:
            from langchain_openai import OpenAIEmbeddings
            logger.info(f"Initializing OpenAIEmbeddings with model: {self.embedding_model_name}")
            self.embedding_model = OpenAIEmbeddings(
                model=self.embedding_model_name,
                openai_api_key=rag_settings.openai_api_key,
                openai_api_base=rag_settings.openai_base_url,
            )
        else:
            try:
                logger.info(f"Resolving embedding model with PolyRAG: {self.embedding_model_name}")
                self.embedding_model = resolve_embedding_model(self.embedding_model_name)
            except Exception as e:
                logger.warning(
                    f"Could not resolve embedding model '{self.embedding_model_name}' ({e}); "
                    f"falling back to FakeEmbeddings(size=1536)"
                )
                from langchain_core.embeddings import FakeEmbeddings
                self.embedding_model = FakeEmbeddings(size=1536)

        # 3. Initialize Vector Store (Milvus Lite default, ChromaDB or InMemory)
        if use_in_memory:
            logger.info("Using InMemoryVectorStore")
            self.vector_store = InMemoryVectorStore(embedding=self.embedding_model)
        elif self.vector_store_type in ("chroma", "chromadb"):
            logger.info(f"Initializing Chroma VectorStore (dir={self.db_path}, collection={self.collection_name})")
            self.vector_store = resolve_vector_store(
                "chroma",
                persist_directory=self.db_path,
                collection_name=self.collection_name,
                embedding=self.embedding_model,
            )
        else:
            logger.info(f"Initializing MilvusLiteVectorStore (db_path={self.db_path}, collection={self.collection_name})")
            self.vector_store = MilvusLiteVectorStore(
                embedding_function=self.embedding_model,
                connection_args={"uri": self.db_path},
                collection_name=self.collection_name,
                auto_id=True,
            )

        # 4. Initialize LLM Client via PolyRAG 0.2.0 resolver
        self.llm_client = None
        if rag_settings.openai_api_key:
            logger.info(f"Initializing LLM client with model: {self.model_name}")
            self.llm_client = resolve_llm_client(
                model_name=self.model_name,
                api_key=rag_settings.openai_api_key,
                base_url=rag_settings.openai_base_url,
            )
        else:
            logger.warning("No OPENAI_API_KEY found. RAG generation will run in retrieval-only mode.")

        # 5. Initialize NaiveRAG Pipeline (PolyRAG 0.2.0)
        self.naive_rag = NaiveRAG(
            chunker=self.chunker,
            embedding_model=self.embedding_model,
            vector_store=self.vector_store,
            llm_client=self.llm_client,
        )

    def count(self) -> int:
        """Return total document count in the active vector collection."""
        if hasattr(self.vector_store, "count"):
            return self.vector_store.count()
        return 0

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

        if force_regenerate and hasattr(self.vector_store, "clear"):
            logger.info("force_regenerate=True: Clearing existing vector store records...")
            self.vector_store.clear()

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
        """Run standard Naive retrieve-then-read RAG pipeline using PolyRAG 0.2.0 NaiveRAG."""
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
