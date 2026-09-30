"""
rag_core - A modular, extensible, and production-ready Retrieval-Augmented Generation library.
"""

from rag_core.chunkers.fixed_size import FixedSizeChunker
from rag_core.chunkers.recursive import RecursiveCharacterChunker
from rag_core.core.interfaces import (
    BaseChunker,
    BaseEmbeddingModel,
    BaseLLMClient,
    BaseVectorStore,
)
from rag_core.core.models import (
    AgentAction,
    AgentResponse,
    AgentStep,
    Chunk,
    Document,
    RAGResponse,
    SearchResult,
)
from rag_core.embeddings.openai import OpenAIEmbedding
from rag_core.embeddings.sentence_transformers import SentenceTransformerEmbedding
from rag_core.exceptions import (
    ConfigurationError,
    IngestionError,
    LLMGenerationError,
    RAGException,
    RetrievalError,
)
from rag_core.llms.openai import OpenAILLM
from rag_core.pipelines.agentic import AgenticRAG
from rag_core.pipelines.naive import NaiveRAG
from rag_core.pipelines.react import ReActAgent
from rag_core.service import AgenticRAGService, RAGService
from rag_core.vector_stores.chroma import ChromaVectorStore
from rag_core.vector_stores.memory import InMemoryVectorStore

__version__ = "0.1.0"

__all__ = [
    # Top-level service facades
    "RAGService",
    "AgenticRAGService",
    # Pipelines
    "NaiveRAG",
    "AgenticRAG",
    "ReActAgent",
    # Chunkers
    "BaseChunker",
    "FixedSizeChunker",
    "RecursiveCharacterChunker",
    # Embeddings
    "BaseEmbeddingModel",
    "SentenceTransformerEmbedding",
    "OpenAIEmbedding",
    # Vector Stores
    "BaseVectorStore",
    "ChromaVectorStore",
    "InMemoryVectorStore",
    # LLM
    "BaseLLMClient",
    "OpenAILLM",
    # Core Data Models
    "Document",
    "Chunk",
    "SearchResult",
    "RAGResponse",
    "AgentAction",
    "AgentStep",
    "AgentResponse",
    # Exceptions
    "RAGException",
    "ConfigurationError",
    "IngestionError",
    "RetrievalError",
    "LLMGenerationError",
]
