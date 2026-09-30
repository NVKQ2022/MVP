"""Vector store interface and ChromaDB implementation.

Delegates to Clean Architecture domain and infrastructure layers.
"""

from src.domain.interfaces.vector_store import VectorStoreInterface
from src.infrastructure.vector_store.chroma_adapter import ChromaVectorStoreAdapter

# Backward-compatible aliases
VectorDB = VectorStoreInterface


class ChromaVectorDB(ChromaVectorStoreAdapter, VectorDB):
    """ChromaDB implementation of VectorDB interface."""
    pass


__all__ = [
    "VectorDB",
    "ChromaVectorDB",
]
