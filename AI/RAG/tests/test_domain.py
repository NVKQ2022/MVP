"""Unit tests for Domain layer entities."""

import unittest

from src.domain.entities.agent import AgentAction, AgentResponse, AgentStep
from src.domain.entities.benchmark import BenchmarkQuestion, BenchmarkResult
from src.domain.entities.document import Chunk, Document
from src.domain.entities.rag_response import RAGResponse
from src.domain.entities.search import SearchResult


class DomainEntitiesTest(unittest.TestCase):
    def test_document_and_chunk(self):
        doc = Document(source="rfc1035.txt", text="Domain Name System", metadata={"author": "Mock"})
        self.assertEqual(doc.source, "rfc1035.txt")
        self.assertEqual(doc.metadata["author"], "Mock")

        chunk = Chunk(source="rfc1035.txt", chunk_id=42, text="DNS Protocol Specification")
        self.assertEqual(chunk.identifier, "rfc1035.txt#42")

        chunk_dict = chunk.to_dict()
        self.assertEqual(chunk_dict["source"], "rfc1035.txt")
        self.assertEqual(chunk_dict["chunk_id"], 42)
        self.assertEqual(chunk_dict["text"], "DNS Protocol Specification")

    def test_search_result(self):
        res = SearchResult(
            score=0.92,
            distance=0.08,
            document={"source": "rfc793.txt", "chunk_id": 12, "text": "TCP Handshake"},
        )
        self.assertEqual(res.source, "rfc793.txt")
        self.assertEqual(res.chunk_id, 12)
        self.assertEqual(res.identifier, "rfc793.txt#12")
        self.assertAlmostEqual(res.score, 0.92)

    def test_rag_response(self):
        resp = RAGResponse(
            question="What is TCP?",
            answer="Transmission Control Protocol",
            took_ms=150,
            confidence=0.95,
        )
        data = resp.to_dict()
        self.assertEqual(data["question"], "What is TCP?")
        self.assertEqual(data["answer"], "Transmission Control Protocol")
        self.assertEqual(data["took_ms"], 150)
        self.assertEqual(data["confidence"], 0.95)

    def test_agent_entities(self):
        action = AgentAction(thought="Need to check RFC 9000", action="search_rfc", action_input={"query": "QUIC"})
        self.assertEqual(action.action, "search_rfc")

        step = AgentStep(
            step_num=1,
            thought=action.thought,
            action=action.action,
            action_input=action.action_input,
            observation="Found 3 chunks",
            chunks_retrieved=3,
        )
        self.assertEqual(step.step_num, 1)
        self.assertEqual(step.chunks_retrieved, 3)

        agent_resp = AgentResponse(
            question="What is QUIC?",
            answer="QUIC is UDP-based",
            trajectory=[step],
            confidence=0.9,
            total_steps=1,
        )
        data = agent_resp.to_dict()
        self.assertEqual(len(data["trajectory"]), 1)
        self.assertEqual(data["total_steps"], 1)

    def test_benchmark_entities(self):
        q = BenchmarkQuestion(id=1, type="single-hop", question="DNS Purpose", keywords=["domain", "mapping"])
        self.assertEqual(q.id, 1)

        result = BenchmarkResult(
            question_id=1,
            question_type="single-hop",
            question="DNS Purpose",
            naive_answer="DNS maps names to IPs",
            agentic_answer="DNS provides domain name mapping",
            naive_hit=False,
            agentic_hit=True,
            naive_latency_ms=200,
            agentic_latency_ms=600,
        )
        self.assertTrue(result.is_agentic_better)
        self.assertFalse(result.is_equal)


if __name__ == "__main__":
    unittest.main()
