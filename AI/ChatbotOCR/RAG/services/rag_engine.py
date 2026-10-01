"""PolyRAG Engine: Integrates polyrag package to ingest and retrieve support KB documents."""

import logging
from pathlib import Path
from typing import Any

from polyrag import (
    PolyRAG,
    RecursiveCharacterChunker,
    SentenceTransformerEmbedding,
    ChromaVectorStore,
    InMemoryVectorStore,
    OpenAILLM,
    RAGResponse,
)
from polyrag.core.interfaces import BaseVectorStore, BaseLLMClient
from polyrag.core.models import AgentResponse

from RAG.config import rag_settings
from RAG.services.document_generator import generate_kb_text_files

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG Orchestrator powered by the PolyRAG package.
    
    Coordinates:
    - Text file document ingestion from knowledge base
    - ChromaDB persistent storage / InMemory fallback
    - Semantic embedding search
    - Response generation (Naive, Advanced with RRF fusion, Agentic)
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

        # 1. Initialize Chunker (sized to preserve complete troubleshooting articles)
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

        # 5. Initialize PolyRAG Application Context
        self.app = PolyRAG(
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
        Ingest all generated .txt files from the KB documents directory into PolyRAG.
        If files do not exist or force_regenerate is True, generates them from knowledge_base.json first.
        """
        target_dir = Path(docs_dir or rag_settings.kb_docs_dir)

        if force_regenerate or not target_dir.exists() or not list(target_dir.glob("*.txt")):
            logger.info(f"Generating KB text files into {target_dir}...")
            generate_kb_text_files(
                json_path=rag_settings.kb_json_path,
                output_dir=target_dir,
            )

        txt_files = sorted(target_dir.glob("*.txt"))
        logger.info(f"Found {len(txt_files)} text files in {target_dir}. Ingesting into vector store...")

        total_chunks = 0
        for f in txt_files:
            text = f.read_text(encoding="utf-8")
            # Parse header metadata if available
            metadata: dict[str, Any] = {"filename": f.name}
            for line in text.split("\n")[:6]:
                if ":" in line:
                    key, val = line.split(":", 1)
                    metadata[key.strip().lower().replace(" ", "_")] = val.strip()

            chunks = self.app.ingest_text(
                text=text,
                source=f.name,
                metadata=metadata,
            )
            total_chunks += len(chunks)

        logger.info(f"Ingested {total_chunks} chunks from {len(txt_files)} files. Total store count: {self.vector_store.count()}")
        return total_chunks

    def search(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        """Perform semantic search over the ingested knowledge base."""
        k = top_k or rag_settings.top_k
        return self.app.retrieve(query=query, top_k=k)

    def query_naive(self, question: str, top_k: int | None = None) -> RAGResponse:
        """Run standard Naive retrieve-then-read RAG pipeline."""
        k = top_k or rag_settings.top_k
        return self.app.query(question=question, top_k=k)

    def query_advanced(
        self,
        question: str,
        top_k: int | None = None,
        num_expanded_queries: int = 3,
        verbose: bool = False,
    ) -> RAGResponse:
        """Run Advanced RAG with multi-query expansion and RRF fusion."""
        k = top_k or rag_settings.top_k
        pipeline = self.app.create_advanced_rag(
            top_k=k,
            num_expanded_queries=num_expanded_queries,
            verbose=verbose,
        )
        return pipeline.execute(question=question, top_k=k)

    def query_agentic(
        self,
        question: str,
        top_k: int | None = None,
        max_rounds: int = 2,
        verbose: bool = False,
    ) -> RAGResponse:
        """Run Agentic RAG with dynamic planning, reflection, and iterative retrieval."""
        k = top_k or rag_settings.top_k
        pipeline = self.app.create_agentic_rag(
            top_k=k,
            max_rounds=max_rounds,
            verbose=verbose,
        )
        return pipeline.execute(question=question, top_k=k, max_rounds=max_rounds)

    def query_react(
        self,
        question: str,
        top_k: int | None = None,
        max_steps: int = 4,
        verbose: bool = False,
    ) -> AgentResponse:
        """Run ReAct agent with Thought-Action-Observation trajectory."""
        k = top_k or rag_settings.top_k
        agent = self.app.create_react_agent(
            max_steps=max_steps,
            default_top_k=k,
            verbose=verbose,
        )
        return agent.execute(question=question, top_k=k, max_steps=max_steps)
