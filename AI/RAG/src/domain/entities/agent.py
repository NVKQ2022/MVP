"""Domain entities for Agentic RAG and ReAct execution."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentAction:
    """Action chosen by an agent."""

    thought: str
    action: str
    action_input: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentStep:
    """A single step in an agent execution trajectory."""

    step_num: int
    thought: str
    action: str
    action_input: dict[str, Any] = field(default_factory=dict)
    observation: str = ""
    chunks_retrieved: int = 0
    took_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_num": self.step_num,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "chunks_retrieved": self.chunks_retrieved,
            "took_ms": self.took_ms,
        }


@dataclass
class AgentResponse:
    """Final output returned by an Agent."""

    question: str
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    retrieved_evidence: list[dict[str, Any]] = field(default_factory=list)
    trajectory: list[AgentStep] = field(default_factory=list)
    reasoning_summary: str = ""
    confidence: float = 1.0
    total_steps: int = 0
    took_ms: int = 0
    llm_calls: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "sources": self.sources,
            "retrieved_evidence": self.retrieved_evidence,
            "trajectory": [s.to_dict() for s in self.trajectory],
            "reasoning_summary": self.reasoning_summary,
            "confidence": self.confidence,
            "total_steps": self.total_steps,
            "took_ms": self.took_ms,
            "llm_calls": self.llm_calls,
        }
