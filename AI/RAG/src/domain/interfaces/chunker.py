"""Abstract interface for document chunking."""

from abc import ABC, abstractmethod


class ChunkerInterface(ABC):
    """Abstract interface for splitting text into chunks."""

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Split text into chunks.

        Args:
            text: Input document text.

        Returns:
            A list of text chunks.
        """
        raise NotImplementedError
