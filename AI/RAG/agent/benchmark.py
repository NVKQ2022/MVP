"""
agent/benchmark.py - 20-Question Evaluation Benchmark comparing Naive RAG vs ReAct Agentic RAG.

Usage:
    python agent/benchmark.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from main import build_llm_client, build_embedding_service, build_vector_db
from config import MODEL_NAME
from agent.react_agent import ReActAgent

# 20 Benchmark questions covering Single-Hop, Multi-Hop, and Comparative RFC domains
BENCHMARK_QUESTIONS = [
    # --- Single-Hop Questions ---
    {
        "id": 1,
        "type": "single-hop",
        "question": "What is the purpose of the Domain Name System (DNS) according to RFC 1035?",
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
        "question": "What handshake latency improvement does TLS 1.3 introduce in RFC 8446?",
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
        "question": "How does QUIC integrate TLS 1.3 cryptographic handshakes to establish secure keys?",
        "keywords": ["TLS 1.3", "8446", "QUIC", "9000", "keys", "crypto"],
    },
    {
        "id": 11,
        "type": "multi-hop",
        "question": "When a DNS query response exceeds 512 bytes over UDP, how does DNS fallback to TCP in RFC 1035 and RFC 793?",
        "keywords": ["512", "truncation", "TC bit", "TCP", "port 53"],
    },
    {
        "id": 12,
        "type": "multi-hop",
        "question": "How does OAuth 2.0 authorization code flow use TLS to protect tokens in transit?",
        "keywords": ["TLS", "HTTPS", "token", "confidentiality", "6749"],
    },
    {
        "id": 13,
        "type": "multi-hop",
        "question": "How does IP packet fragmentation in RFC 791 relate to TCP Maximum Segment Size (MSS) in RFC 793?",
        "keywords": ["fragmentation", "MTU", "MSS", "header", "offset"],
    },
    {
        "id": 14,
        "type": "multi-hop",
        "question": "Which RFC specifies JSON syntax, and how is application/json declared in HTTP request headers according to RFC 9110?",
        "keywords": ["8259", "application/json", "Content-Type", "9110"],
    },
    {
        "id": 15,
        "type": "multi-hop",
        "question": "How does QUIC connection migration preserve active connections when a client changes IP addresses?",
        "keywords": ["Connection ID", "CID", "path validation", "probe", "migration"],
    },
    {
        "id": 16,
        "type": "multi-hop",
        "question": "Compare the keep-alive and connection termination mechanisms between TCP (RFC 793) and QUIC (RFC 9000).",
        "keywords": ["FIN", "RST", "CONNECTION_CLOSE", "idle timeout", "silent close"],
    },

    # --- Comparative Questions ---
    {
        "id": 17,
        "type": "comparative",
        "question": "What are the security advantages of TLS 1.3 (RFC 8446) cipher suites compared to legacy static RSA handshakes?",
        "keywords": ["forward secrecy", "AEAD", "deprecated", "RSA key exchange removed"],
    },
    {
        "id": 18,
        "type": "comparative",
        "question": "Explain the difference between idempotent and safe HTTP methods in RFC 9110 with examples.",
        "keywords": ["GET", "PUT", "DELETE", "POST", "idempotent", "safe"],
    },
    {
        "id": 19,
        "type": "comparative",
        "question": "How do DNS authoritative servers and recursive resolvers interact to resolve queries in RFC 1035?",
        "keywords": ["recursive", "iterative", "authoritative", "root", "cache"],
    },
    {
        "id": 20,
        "type": "comparative",
        "question": "How does OAuth 2.0 refresh token rotation mitigate risk compared to long-lived access tokens?",
        "keywords": ["refresh token", "access token", "expiration", "scope", "revocation"],
    },
]


def score_answer(answer: str, keywords: list[str]) -> float:
    """Computes keyword / fact coverage ratio."""
    low = answer.lower()
    matches = sum(1 for kw in keywords if kw.lower() in low)
    return matches / len(keywords) if keywords else 1.0


def run_benchmark():
    print("=" * 75)
    print("      RUNNING 20-QUESTION BENCHMARK: NAIVE RAG VS REACT AGENTIC RAG")
    print("=" * 75)

    client = build_llm_client()
    embedding_service = build_embedding_service()
    vector_db = build_vector_db()

    agent = ReActAgent(
        client=client,
        embedding_service=embedding_service,
        vector_db=vector_db,
        model_name=MODEL_NAME,
        max_steps=4,
        default_top_k=3,
    )

    naive_scores = []
    agent_scores = []

    print(f"{'ID':<3} | {'Type':<12} | {'Naive RAG':<12} | {'ReAct Agent':<12} | {'Improvement':<12}")
    print("-" * 65)

    for item in BENCHMARK_QUESTIONS:
        qid = item["id"]
        qtype = item["type"]
        qtext = item["question"]
        kws = item["keywords"]

        # Run Naive RAG
        naive_out = agent.query_naive(qtext, top_k=3)
        naive_s = score_answer(naive_out["answer"], kws)
        naive_scores.append(naive_s)

        # Run ReAct Agentic RAG
        agent_out = agent.query(qtext, top_k=3, max_steps=4)
        agent_s = score_answer(agent_out.answer, kws)
        agent_scores.append(agent_s)

        diff = agent_s - naive_s
        diff_str = f"+{diff*100:.1f}%" if diff >= 0 else f"{diff*100:.1f}%"
        print(f"{qid:<3} | {qtype:<12} | {naive_s*100:>6.1f}%      | {agent_s*100:>6.1f}%      | {diff_str:<12}")

    avg_naive = sum(naive_scores) / len(naive_scores)
    avg_agent = sum(agent_scores) / len(agent_scores)
    improvement = ((avg_agent - avg_naive) / max(0.001, avg_naive)) * 100

    print("=" * 65)
    print(f"Average Naive RAG Score   : {avg_naive*100:.2f}%")
    print(f"Average ReAct Agent Score : {avg_agent*100:.2f}%")
    print(f"Relative Gain             : +{improvement:.2f}%")
    print("=" * 65)

    if improvement >= 20.0:
        print("✓ SUCCESS: ReAct Agent achieved >= 20% improvement over Naive RAG!")


if __name__ == "__main__":
    run_benchmark()
