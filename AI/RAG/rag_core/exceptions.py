"""Custom Exception Hierarchy for rag_core."""


class RAGException(Exception):
    """Base exception for all errors raised in rag_core."""
    pass


class ConfigurationError(RAGException):
    """Raised when environment variables or configurations are missing or invalid."""
    pass


class IngestionError(RAGException):
    """Raised when document ingestion or parsing fails."""
    pass


class RetrievalError(RAGException):
    """Raised when vector database search or connection fails."""
    pass


class LLMGenerationError(RAGException):
    """Raised when LLM client completion or response parsing fails."""
    pass
