"""ReAct Agent - delegates to Clean Architecture use cases."""

from typing import Any

from src.application.use_cases.react_agent import ReActAgentUseCase
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.domain.interfaces.llm import LLMClientInterface
from src.domain.interfaces.vector_store import VectorStoreInterface
from src.infrastructure.llm.openai_adapter import OpenAILLMAdapter


class ReActAgent:
    """ReAct (Reasoning + Acting) Agent for Technical RFC Question Answering."""

    def __init__(
        self,
        client: Any,
        embedding_service: EmbeddingModelInterface,
        vector_db: VectorStoreInterface,
        model_name: str,
        max_steps: int = 4,
        default_top_k: int = 5,
    ) -> None:
        if client is not None and not isinstance(client, LLMClientInterface):
            self.llm_client = OpenAILLMAdapter(model_name=model_name, client=client)
        else:
            self.llm_client = client

        self.use_case = ReActAgentUseCase(
            llm_client=self.llm_client,
            embedding_model=embedding_service,
            vector_store=vector_db,
            max_steps=max_steps,
            default_top_k=default_top_k,
        )

    def query(
        self,
        question: str,
        top_k: int | None = None,
        max_steps: int | None = None,
    ):
        """Execute ReAct workflow."""
        return self.use_case.execute(
            question=question,
            top_k=top_k,
            max_steps=max_steps,
        )


__all__ = ["ReActAgent"]
