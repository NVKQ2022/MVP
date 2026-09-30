"""Embedding service interfaces and implementations.

Delegates to Clean Architecture domain and infrastructure layers.
"""

from typing import Any
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.infrastructure.embedding.openai_embedding import OpenAIEmbeddingAdapter
from src.infrastructure.embedding.sentence_transformer import SentenceTransformerEmbeddingAdapter


class EmbeddingService(EmbeddingModelInterface):
    """Abstract interface and smart factory for embedding implementations."""

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls is EmbeddingService:
            # Auto-dispatch based on model name or default
            model_name = kwargs.get("model_name", "all-MiniLM-L6-v2")
            if "text-embedding" in model_name:
                return OpenAIEmbeddingAdapter(*args, **kwargs)
            return SentenceTransformerEmbeddingAdapter(*args, **kwargs)
        return super().__new__(cls)


# Backward-compatible class aliases
HFEmbeddingService = SentenceTransformerEmbeddingAdapter
OpenAIEmbeddingService = OpenAIEmbeddingAdapter

__all__ = [
    "EmbeddingService",
    "HFEmbeddingService",
    "OpenAIEmbeddingService",
]
