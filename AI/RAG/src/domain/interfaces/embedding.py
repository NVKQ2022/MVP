"""Abstract interface for text embedding models."""

from abc import ABC, abstractmethod


class EmbeddingModelInterface(ABC):
    """Abstract interface for embedding implementations."""

    @property
    @abstractmethod
    def dim(self) -> int:
        """Return the dimensionality of the embedding vector."""
        raise NotImplementedError

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for a single text.

        Args:
            text: Input string.

        Returns:
            List of floats representing the embedding vector.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 128,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of strings.
            batch_size: Batch size for model inference.

        Returns:
            List of embedding vectors.
        """
        raise NotImplementedError
