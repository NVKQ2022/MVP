"""Abstract interface for Language Model completions."""

from abc import ABC, abstractmethod
from typing import Any


class LLMClientInterface(ABC):
    """Abstract interface for interacting with LLMs."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the active model name."""
        raise NotImplementedError

    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate a text completion for a prompt."""
        raise NotImplementedError

    @abstractmethod
    def complete_json(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        """Generate and parse a JSON completion for a prompt."""
        raise NotImplementedError

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Generate a chat completion for conversation messages."""
        raise NotImplementedError
