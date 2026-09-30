"""Abstract interface for Vector Store operations."""

from abc import ABC, abstractmethod
from typing import Any


class VectorStoreInterface(ABC):
    """Abstract interface for vector database storage and retrieval."""

    @abstractmethod
    def clear(self) -> None:
        """Clear all records from the store / collection."""
        raise NotImplementedError

    @abstractmethod
    def add_documents(
        self,
        vectors: list[list[float]],
        documents: list[dict[str, Any]],
        batch_size: int = 5000,
    ) -> None:
        """Add pre-computed vectors and document metadata.

        Args:
            vectors: List of embedding vectors.
            documents: List of document metadata dictionaries (must have 'text').
            batch_size: Batch size for inserting documents.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search nearest neighbors for a query vector.

        Args:
            query_vector: Embedding vector of query.
            top_k: Number of nearest items to return.

        Returns:
            List of dicts with 'score', 'distance', 'document'.
        """
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Return total number of items stored in collection."""
        raise NotImplementedError

    @abstractmethod
    def peek(self, limit: int = 5) -> Any:
        """Preview sample items from store."""
        raise NotImplementedError
