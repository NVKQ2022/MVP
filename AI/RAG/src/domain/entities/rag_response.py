"""Domain entity for RAG Query responses."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RAGResponse:
    """Represents the end-to-end response of a RAG query."""

    question: str
    answer: str
    context: str = ""
    sources: list[dict[str, Any]] = field(default_factory=list)
    took_ms: int = 0
    confidence: float = 1.0
    reasoning_summary: str = ""
    agent_log: list[dict[str, Any]] = field(default_factory=list)
    llm_calls: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "context": self.context,
            "sources": self.sources,
            "took_ms": self.took_ms,
            "confidence": self.confidence,
            "reasoning_summary": self.reasoning_summary,
            "agent_log": self.agent_log,
            "llm_calls": self.llm_calls,
        }
