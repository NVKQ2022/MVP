
from abc import ABC, abstractmethod


class ChunkingService(ABC):
    """
    Abstract interface for document chunking strategies.
    """

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """
        Split text into chunks.

        Args:
            text: Input document text.

        Returns:
            A list of text chunks.
        """
        raise NotImplementedError


class FixedSizeChunkingService(ChunkingService):
    """
    Split text into fixed-size, overlapping character chunks.
    """

    def __init__(
        self,
        chunk_size: int = 300,
        overlap: int = 30,
        drop_empty: bool = True,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap must be >= 0")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap
        self.drop_empty = drop_empty

    def chunk(self, text: str) -> list[str]:
        """
        Split text into overlapping fixed-size chunks.
        """
        if self.drop_empty and not text.strip():
            return []

        step = self.chunk_size - self.overlap
        chunks: list[str] = []

        for start in range(0, len(text), step):
            chunk = text[start:start + self.chunk_size]

            if not self.drop_empty or chunk.strip():
                chunks.append(chunk)

            if start + self.chunk_size >= len(text):
                break

        return chunks
