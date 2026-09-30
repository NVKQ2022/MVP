"""Domain entities for Benchmarking and Evaluation."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BenchmarkQuestion:
    """A benchmark evaluation question."""

    id: int
    type: str  # "single-hop" | "multi-hop" | "comparative"
    question: str
    keywords: list[str] = field(default_factory=list)


@dataclass
class BenchmarkResult:
    """Evaluation result comparing Naive and Agentic RAG for a question."""

    question_id: int
    question_type: str
    question: str
    naive_answer: str
    agentic_answer: str
    naive_hit: bool
    agentic_hit: bool
    naive_latency_ms: int
    agentic_latency_ms: int
    agentic_steps: int = 1
    agentic_confidence: float = 1.0
    matched_naive_keywords: list[str] = field(default_factory=list)
    matched_agentic_keywords: list[str] = field(default_factory=list)

    @property
    def is_agentic_better(self) -> bool:
        return self.agentic_hit and not self.naive_hit

    @property
    def is_equal(self) -> bool:
        return self.agentic_hit == self.naive_hit
