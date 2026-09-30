"""Unit tests for Application Use Cases with test doubles."""

from typing import Any
import unittest

from src.application.use_cases.agentic_rag import AgenticRAGUseCase
from src.application.use_cases.evaluate_benchmark import EvaluateBenchmarkUseCase
from src.application.use_cases.ingest_documents import IngestDocumentsUseCase
from src.application.use_cases.naive_rag import NaiveRAGUseCase
from src.domain.interfaces.chunker import ChunkerInterface
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.domain.interfaces.llm import LLMClientInterface
from src.domain.interfaces.vector_store import VectorStoreInterface


class MockChunker(ChunkerInterface):
    def chunk(self, text: str) -> list[str]:
        return [s.strip() for s in text.split("\n\n") if s.strip()]


class MockEmbeddingModel(EmbeddingModelInterface):
    @property
    def dim(self) -> int:
        return 4

    def embed_text(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3, 0.4]

    def embed_batch(self, texts: list[str], batch_size: int = 128) -> list[list[float]]:
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]


class MockVectorStore(VectorStoreInterface):
    def __init__(self):
        self.docs: list[dict[str, Any]] = []

    def clear(self) -> None:
        self.docs = []

    def add_documents(
        self,
        vectors: list[list[float]],
        documents: list[dict[str, Any]],
        batch_size: int = 5000,
    ) -> None:
        self.docs.extend(documents)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        results = []
        for d in self.docs[:top_k]:
            results.append({"score": 0.95, "distance": 0.05, "document": d})
        return results

    def count(self) -> int:
        return len(self.docs)

    def peek(self, limit: int = 5) -> Any:
        return {"documents": [d["text"] for d in self.docs[:limit]]}


class MockLLMClient(LLMClientInterface):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.responses = responses or {}
        self._model_name = "mock-gpt"

    @property
    def model_name(self) -> str:
        return self._model_name

    def complete(self, prompt: str, **kwargs: Any) -> str:
        for k, v in self.responses.items():
            if k in prompt and isinstance(v, str):
                return v
        return "Grounded answer from mock LLM citing [rfc1035.txt#0]."

    def complete_json(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        for k, v in self.responses.items():
            if k in prompt and isinstance(v, dict):
                return v
        return {
            "retrieval_needed": True,
            "query": "DNS RFC 1035 UDP limit",
            "reason": "Technical protocol question",
            "enough": True,
            "confidence": 0.95,
            "answer": "Grounded answer from JSON [rfc1035.txt#0]",
        }

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return self.complete(messages[-1]["content"])


class ApplicationUseCasesTest(unittest.TestCase):
    def setUp(self):
        self.chunker = MockChunker()
        self.embedding = MockEmbeddingModel()
        self.vector_store = MockVectorStore()
        self.llm = MockLLMClient()

    def test_ingest_documents_use_case(self):
        use_case = IngestDocumentsUseCase(
            chunker=self.chunker,
            embedding_model=self.embedding,
            vector_store=self.vector_store,
        )
        text = "First paragraph about RFC.\n\nSecond paragraph about DNS."
        ingested = use_case.ingest_text(text, source="rfc1035.txt")
        self.assertEqual(len(ingested), 2)
        self.assertEqual(self.vector_store.count(), 2)

    def test_naive_rag_use_case(self):
        # Ingest first
        ingest = IngestDocumentsUseCase(self.chunker, self.embedding, self.vector_store)
        ingest.ingest_text("RFC 1035 defines the DNS protocol.", source="rfc1035.txt")

        naive_rag = NaiveRAGUseCase(
            embedding_model=self.embedding,
            vector_store=self.vector_store,
            llm_client=self.llm,
        )

        resp = naive_rag.execute("What is RFC 1035?")
        self.assertEqual(resp.question, "What is RFC 1035?")
        self.assertIn("Grounded answer", resp.answer)
        self.assertEqual(len(resp.sources), 1)
        self.assertEqual(resp.sources[0]["source"], "rfc1035.txt")

    def test_agentic_rag_use_case(self):
        ingest = IngestDocumentsUseCase(self.chunker, self.embedding, self.vector_store)
        ingest.ingest_text("RFC 1035 sets 512-byte UDP limit with TC bit.", source="rfc1035.txt")

        naive_rag = NaiveRAGUseCase(self.embedding, self.vector_store, self.llm)
        agentic_rag = AgenticRAGUseCase(
            naive_rag=naive_rag,
            llm_client=self.llm,
            top_k=2,
            max_rounds=2,
            verbose=False,
        )

        resp = agentic_rag.execute("What is the DNS UDP limit?")
        self.assertIn("Grounded answer", resp.answer)
        self.assertGreater(len(resp.agent_log), 0)
        self.assertGreater(resp.confidence, 0.8)

    def test_evaluate_benchmark_use_case(self):
        ingest = IngestDocumentsUseCase(self.chunker, self.embedding, self.vector_store)
        ingest.ingest_text("RFC 1035 provides domain name mapping.", source="rfc1035.txt")

        naive_rag = NaiveRAGUseCase(self.embedding, self.vector_store, self.llm)
        agentic_rag = AgenticRAGUseCase(naive_rag, self.llm, top_k=2, verbose=False)

        eval_use_case = EvaluateBenchmarkUseCase(
            naive_rag=naive_rag,
            agentic_rag=agentic_rag,
            questions=[
                {
                    "id": 1,
                    "type": "single-hop",
                    "question": "What is the purpose of DNS?",
                    "keywords": ["domain", "name"],
                }
            ],
        )

        summary = eval_use_case.execute()
        self.assertEqual(summary["total_questions"], 1)
        self.assertIn("naive_accuracy", summary)
        self.assertIn("agentic_accuracy", summary)


if __name__ == "__main__":
    unittest.main()
