"""Pydantic schemas for Web API endpoints."""

from typing import Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request payload for vector search or RAG query."""

    query: str
    top_k: int = Field(default=5, gt=0)


class AgenticQueryRequest(BaseModel):
    """Request payload for agentic RAG query."""

    query: str
    top_k: int = Field(default=3, gt=0)
    max_rounds: int = Field(default=3, gt=0, le=10)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    embedding_dim: int | None = None
    vector_collection: str | None = None
    vector_count: int = 0
    llm_model: str | None = None
    llm_available: bool = False
