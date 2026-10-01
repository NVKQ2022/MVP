"""Configuration placeholder for RAG module."""

import os
from pydantic import BaseModel, Field


class RAGSettings(BaseModel):
    """RAG settings loaded from environment or defaults."""

    rag_enabled: bool = Field(
        default_factory=lambda: os.getenv("RAG_ENABLED", "false").lower() in ("true", "1", "yes")
    )


rag_settings = RAGSettings()
