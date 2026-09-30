"""Use case for running the 20-Question Benchmark Evaluation."""

import time
from typing import Any

from src.application.use_cases.agentic_rag import AgenticRAGUseCase
from src.application.use_cases.naive_rag import NaiveRAGUseCase
from src.domain.entities.benchmark import BenchmarkQuestion, BenchmarkResult

DEFAULT_BENCHMARK_QUESTIONS: list[dict[str, Any]] = [
    # --- Single-Hop Questions ---
    {
        "id": 1,
        "type": "single-hop",
        "question": "What is the primary purpose of the Domain Name System (DNS) according to RFC 1035?",
        "keywords": ["domain", "name", "mapping", "host", "1035"],
    },
    {
        "id": 2,
        "type": "single-hop",
        "question": "What are the four authorization grant types defined in OAuth 2.0 (RFC 6749)?",
        "keywords": ["authorization code", "implicit", "password", "client credentials"],
    },
    {
        "id": 3,
        "type": "single-hop",
        "question": "What is the minimum and maximum header size of an IPv4 packet in RFC 791?",
        "keywords": ["20", "60", "bytes", "header", "options"],
    },
    {
        "id": 4,
        "type": "single-hop",
        "question": "Explain the flags used during the TCP three-way handshake in RFC 793.",
        "keywords": ["SYN", "ACK", "handshake", "sequence"],
    },
    {
        "id": 5,
        "type": "single-hop",
        "question": "List the valid primitive data types in JSON syntax according to RFC 8259.",
        "keywords": ["object", "array", "string", "number", "boolean", "null"],
    },
    {
        "id": 6,
        "type": "single-hop",
        "question": "What handshake round-trip latency improvement does TLS 1.3 introduce in RFC 8446?",
        "keywords": ["1-RTT", "0-RTT", "round trip", "latency"],
    },
    {
        "id": 7,
        "type": "single-hop",
        "question": "What transport layer protocol is QUIC built on according to RFC 9000?",
        "keywords": ["UDP", "multiplexed", "9000"],
    },
    {
        "id": 8,
        "type": "single-hop",
        "question": "What does the 429 status code represent in HTTP semantics (RFC 9110)?",
        "keywords": ["Too Many Requests", "rate limit", "429"],
    },
    # --- Multi-Hop Questions ---
    {
        "id": 9,
        "type": "multi-hop",
        "question": "What transport protocol does HTTP/3 rely on, and what RFC defines its connection establishment mechanism?",
        "keywords": ["QUIC", "9000", "UDP", "handshake"],
    },
    {
        "id": 10,
        "type": "multi-hop",
        "question": "When a DNS response exceeds the 512-byte UDP limit in RFC 1035, which header bit is set, and what TCP flags defined in RFC 793 are sent to initiate the fallback connection?",
        "keywords": ["TC", "truncation", "SYN", "793", "TCP"],
    },
    {
        "id": 11,
        "type": "multi-hop",
        "question": "In an OAuth 2.0 authorization code flow (RFC 6749), why is TLS 1.3 (RFC 8446) required for protecting the token exchange endpoint?",
        "keywords": ["confidentiality", "token", "eavesdropping", "TLS", "secret"],
    },
    {
        "id": 12,
        "type": "multi-hop",
        "question": "How does TCP connection termination in RFC 793 differ from IPv4 packet fragmentation in RFC 791 regarding packet control fields?",
        "keywords": ["FIN", "flags", "fragment offset", "identification", "MF"],
    },
    {
        "id": 13,
        "type": "multi-hop",
        "question": "How does QUIC (RFC 9000) resolve the head-of-line blocking issue present in HTTP/2 running over TCP (RFC 793)?",
        "keywords": ["stream", "multiplexing", "independent", "head-of-line", "loss"],
    },
    {
        "id": 14,
        "type": "multi-hop",
        "question": "What vulnerability does 0-RTT data in TLS 1.3 (RFC 8446) introduce, and how does HTTP semantics (RFC 9110) recommend mitigating it with safe methods?",
        "keywords": ["replay", "GET", "safe", "idempotent", "0-RTT"],
    },
    {
        "id": 15,
        "type": "multi-hop",
        "question": "What IPv4 header field in RFC 791 prevents packet looping, and what TCP mechanism in RFC 793 ensures reliability if that packet is dropped?",
        "keywords": ["TTL", "Time to Live", "retransmission", "timeout", "ACK"],
    },
    {
        "id": 16,
        "type": "multi-hop",
        "question": "When querying an MX record in DNS (RFC 1035), what protocol and port from HTTP/TCP standards is typically not used for mail transfer?",
        "keywords": ["SMTP", "25", "TCP", "mail"],
    },
    # --- Comparative / Edge Questions ---
    {
        "id": 17,
        "type": "comparative",
        "question": "Compare the connection establishment mechanisms of TCP (RFC 793) and QUIC (RFC 9000) in terms of round-trip times (RTTs).",
        "keywords": ["3-way", "1-RTT", "0-RTT", "handshake", "latency"],
    },
    {
        "id": 18,
        "type": "comparative",
        "question": "How does token authentication in OAuth 2.0 (RFC 6749) map to the HTTP Authorization header semantics in RFC 9110?",
        "keywords": ["Bearer", "Authorization", "header", "credentials"],
    },
    {
        "id": 19,
        "type": "comparative",
        "question": "Contrast the character encoding and string rules between JSON (RFC 8259) and DNS domain name labels (RFC 1035).",
        "keywords": ["UTF-8", "ASCII", "octet", "63", "escape"],
    },
    {
        "id": 20,
        "type": "comparative",
        "question": "What security guarantees does TLS 1.3 (RFC 8446) provide that are entirely absent in base IPv4 (RFC 791) and TCP (RFC 793)?",
        "keywords": ["encryption", "confidentiality", "integrity", "authentication", "plaintext"],
    },
]


class EvaluateBenchmarkUseCase:
    """Evaluates 20 RFC questions across Naive and Agentic RAG."""

    def __init__(
        self,
        naive_rag: NaiveRAGUseCase,
        agentic_rag: AgenticRAGUseCase,
        questions: list[dict[str, Any]] | None = None,
    ) -> None:
        self.naive_rag = naive_rag
        self.agentic_rag = agentic_rag
        self.questions = questions or DEFAULT_BENCHMARK_QUESTIONS

    def _check_keywords(self, text: str, keywords: list[str]) -> tuple[bool, list[str]]:
        """Check keyword match presence in text."""
        lower_text = text.lower()
        matched = [k for k in keywords if k.lower() in lower_text]
        # At least 40% of target keywords should be present for a hit
        hit = len(matched) >= max(1, int(len(keywords) * 0.40))
        return hit, matched

    def execute(
        self,
        top_k: int = 3,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Execute benchmark evaluation across questions."""
        q_list = self.questions[:limit] if limit else self.questions
        results: list[BenchmarkResult] = []

        print(f"\nRunning Benchmark Evaluation on {len(q_list)} Questions...")
        print("=" * 70)

        for q in q_list:
            qid = q["id"]
            qtype = q["type"]
            qtext = q["question"]
            keywords = q["keywords"]

            print(f"\n[{qid}/20] ({qtype.upper()}) {qtext}")

            # 1. Naive RAG
            t0 = time.time()
            naive_resp = self.naive_rag.execute(qtext, top_k=top_k)
            naive_latency = int((time.time() - t0) * 1000)
            naive_hit, naive_matched = self._check_keywords(naive_resp.answer, keywords)

            # 2. Agentic RAG
            t0 = time.time()
            agentic_resp = self.agentic_rag.execute(qtext)
            agentic_latency = int((time.time() - t0) * 1000)
            agentic_hit, agentic_matched = self._check_keywords(agentic_resp.answer, keywords)

            # Step count
            steps = len([l for l in agentic_resp.agent_log if l.get("action") == "VECTOR_SEARCH"]) or 1

            res = BenchmarkResult(
                question_id=qid,
                question_type=qtype,
                question=qtext,
                naive_answer=naive_resp.answer,
                agentic_answer=agentic_resp.answer,
                naive_hit=naive_hit,
                agentic_hit=agentic_hit,
                naive_latency_ms=naive_latency,
                agentic_latency_ms=agentic_latency,
                agentic_steps=steps,
                agentic_confidence=agentic_resp.confidence,
                matched_naive_keywords=naive_matched,
                matched_agentic_keywords=agentic_matched,
            )
            results.append(res)

            status = "AGENTIC WIN" if res.is_agentic_better else ("TIED" if res.is_equal else "NAIVE WIN")
            print(f"    Naive Hit: {naive_hit} | Agentic Hit: {agentic_hit} -> [{status}]")

        # Compute summary metrics
        total = len(results)
        naive_hits = sum(1 for r in results if r.naive_hit)
        agentic_hits = sum(1 for r in results if r.agentic_hit)
        naive_acc = (naive_hits / total) * 100 if total > 0 else 0.0
        agentic_acc = (agentic_hits / total) * 100 if total > 0 else 0.0
        improvement = agentic_acc - naive_acc

        avg_naive_lat = sum(r.naive_latency_ms for r in results) / total if total > 0 else 0
        avg_agentic_lat = sum(r.agentic_latency_ms for r in results) / total if total > 0 else 0

        summary = {
            "total_questions": total,
            "naive_hits": naive_hits,
            "agentic_hits": agentic_hits,
            "naive_accuracy": round(naive_acc, 1),
            "agentic_accuracy": round(agentic_acc, 1),
            "improvement": round(improvement, 1),
            "avg_naive_latency_ms": int(avg_naive_lat),
            "avg_agentic_latency_ms": int(avg_agentic_lat),
            "results": results,
        }
        return summary
