"""
agent/models.py - Pydantic models for the ReAct Agentic RAG system.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """Represents a single retrieved text chunk with metadata."""
    source: str
    chunk_id: int | str
    text: str
    score: float = 0.0
    distance: float = 0.0
    round_num: int = 1

    @property
    def identifier(self) -> str:
        return f"{self.source}#{self.chunk_id}"


class AgentAction(BaseModel):
    """Action chosen by the ReAct agent."""
    thought: str = Field(description="Reasoning about the current state and what to do next")
    action: str = Field(description="Tool name to execute, or 'final_answer'")
    action_input: dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool")


class AgentStep(BaseModel):
    """A single step in the ReAct execution trajectory."""
    step_num: int
    thought: str
    action: str
    action_input: dict[str, Any] = Field(default_factory=dict)
    observation: str = ""
    chunks_retrieved: int = 0


class AgentResponse(BaseModel):
    """Final output returned by the ReAct Agent."""
    question: str
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    retrieved_evidence: list[dict[str, Any]] = Field(default_factory=list)
    trajectory: list[AgentStep] = Field(default_factory=list)
    reasoning_summary: str = ""
    confidence: float = 1.0
    total_steps: int = 0
    took_ms: int = 0
