"""Domain entity for Vector Search results."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchResult:
    """Represents a search hit from the vector store."""

    score: float
    distance: float
    document: dict[str, Any] = field(default_factory=dict)

    @property
    def source(self) -> str:
        return self.document.get("source", "unknown")

    @property
    def chunk_id(self) -> Any:
        return self.document.get("chunk_id", "")

    @property
    def text(self) -> str:
        return self.document.get("text", "")

    @property
    def identifier(self) -> str:
        return f"{self.source}#{self.chunk_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "distance": self.distance,
            "document": self.document,
        }
