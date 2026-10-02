"""PolyRAG Engine: Integrates polyrag 0.1.5 NaiveRAG with Milvus Lite vector store."""

import logging
from pathlib import Path
from typing import Any

from polyrag import (
    NaiveRAG,
    RecursiveCharacterChunker,
    SentenceTransformerEmbedding,
    MilvusLiteVectorStore,
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
    - Milvus Lite embedded vector store (with ChromaDB & InMemory fallback)
    - Semantic dense embedding search (SentenceTransformers / OpenAI)
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

        # 3. Initialize Vector Store (Milvus Lite default, ChromaDB or InMemory)
        if use_in_memory:
            logger.info("Using InMemoryVectorStore")
            self.vector_store: BaseVectorStore = InMemoryVectorStore()
        elif self.vector_store_type in ("chroma", "chromadb"):
            logger.info(f"Initializing ChromaVectorStore (dir={self.db_path}, collection={self.collection_name})")
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            self.vector_store = ChromaVectorStore(
                persist_directory=self.db_path,
                collection_name=self.collection_name,
            )
        else:
            logger.info(f"Initializing MilvusLiteVectorStore (db_path={self.db_path}, collection={self.collection_name})")
            emb_dim = getattr(self.embedding_model, "dim", None)
            self.vector_store = MilvusLiteVectorStore(
                db_path=self.db_path,
                collection_name=self.collection_name,
                dimension=emb_dim,
            )
            self._ensure_milvus_loaded()

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

    def _ensure_milvus_loaded(self) -> None:
        """Ensure collection is loaded into memory if using Milvus / Milvus Lite."""
        if hasattr(self.vector_store, "client") and hasattr(self.vector_store, "collection_name"):
            try:
                client = self.vector_store.client
                col_name = self.vector_store.collection_name
                if client.has_collection(collection_name=col_name):
                    load_state = client.get_load_state(collection_name=col_name)
                    state_val = str(load_state.get("state", ""))
                    if "loaded" not in state_val.lower():
                        client.load_collection(collection_name=col_name)
                        logger.debug(f"Loaded Milvus collection '{col_name}' into memory.")
            except Exception as e:
                logger.warning(f"Could not verify/load Milvus collection state: {e}")

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
        self._ensure_milvus_loaded()
        k = top_k or rag_settings.top_k
        return self.naive_rag.retrieve(query=query, top_k=k)

    def query_naive(self, question: str, top_k: int | None = None) -> RAGResponse:
        """Run standard Naive retrieve-then-read RAG pipeline using PolyRAG 0.1.5 NaiveRAG."""
        self._ensure_milvus_loaded()
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
