"""Agentic RAG Service.

Delegates to Clean Architecture application layer while preserving backward compatibility.
"""

from typing import Any

from rag_service import RAGService
from src.application.use_cases.agentic_rag import AgenticRAGUseCase


class AgenticRAGService:
    """Agentic RAG Service with planning, iterative search, and self-reflection."""

    def __init__(
        self,
        rag_service: RAGService,
        top_k: int = 3,
        max_rounds: int = 2,
        verbose: bool = True,
    ) -> None:
        self.rag_service = rag_service
        self.top_k = top_k
        self.max_rounds = max_rounds
        self.verbose = verbose

        self.use_case = AgenticRAGUseCase(
            naive_rag=rag_service.naive_rag,
            llm_client=rag_service.llm_client,
            top_k=top_k,
            max_rounds=max_rounds,
            verbose=verbose,
        )

    def decide_retrieval(self, question: str) -> dict[str, Any]:
        """Decide whether retrieval is needed & rewrite query."""
        return self.use_case.decide_retrieval(question)

    def reflect_and_evaluate(
        self,
        question: str,
        context: str,
        round_number: int,
    ) -> dict[str, Any]:
        """Evaluate evidence sufficiency and synthesize grounded answer."""
        return self.use_case.reflect_and_evaluate(
            question=question,
            context=context,
            round_number=round_number,
        )

    def direct_answer(self, question: str) -> str:
        """Direct answer for non-retrieval conversational queries."""
        return self.use_case.direct_answer(question)

    def query(self, question: str) -> dict[str, Any]:
        """Run full Agentic RAG pipeline."""
        return self.use_case.execute(question).to_dict()


__all__ = ["AgenticRAGService"]