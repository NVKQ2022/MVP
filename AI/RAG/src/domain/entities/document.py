"""Domain entities for Documents and Chunks."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """Represents a raw or loaded document."""

    source: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    doc_id: str | None = None


@dataclass
class Chunk:
    """Represents a segmented text chunk from a document."""

    source: str
    chunk_id: int | str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    chunk_uuid: str | None = None

    @property
    def identifier(self) -> str:
        """Return canonical chunk identifier (e.g., rfc1035.txt#42)."""
        return f"{self.source}#{self.chunk_id}"

    def to_dict(self) -> dict[str, Any]:
        """Convert chunk to dictionary format."""
        data = {
            "source": self.source,
            "chunk_id": self.chunk_id,
            "text": self.text,
            **self.metadata,
        }
        if self.chunk_uuid:
            data["_id"] = self.chunk_uuid
        return data
