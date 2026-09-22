# benchmark.py

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import (
    build_chunking_service,
    build_embedding_service,
    build_llm_client,
    build_vector_db,
)
from rag_service import RAGService
from agenticRag import AgenticRAGService

# 20 Benchmark questions covering Single-Hop, Multi-Hop, and Comparative RFC domains
BENCHMARK_QUESTIONS = [
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
        "question": "How does QUIC integrate TLS 1.3 cryptographic handshakes to establish secure keys?",
        "keywords": ["TLS 1.3", "8446", "QUIC", "9000", "keys", "crypto"],
    },
    {
        "id": 11,
        "type": "multi-hop",
        "question": "When a DNS response exceeds the UDP size limit in RFC 1035, which header bit is set, and what TCP flags defined in RFC 793 are sent to initiate the fallback connection?",
        "keywords": ["512", "truncation", "TC", "TCP", "SYN", "ACK"],
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
        "keywords": ["forward secrecy", "AEAD", "deprecated", "RSA"],
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
    """Calculate fact/keyword coverage score (0.0 to 1.0)."""
    if not answer or not keywords:
        return 0.0
    lower_ans = answer.lower()
    matches = sum(1 for kw in keywords if kw.lower() in lower_ans)
    return matches / len(keywords)


def run_naive_rag(rag_service: RAGService, question: str, top_k: int = 3) -> dict:
    """Standard naive retrieve-then-read RAG."""
    t0 = time.time()
    results = rag_service.retrieve(question, top_k=top_k)
    context = rag_service.format_context(results)

    prompt = (
        "Use the following context to answer the question. "
        "If the answer is not in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

    client = rag_service.client
    model_name = rag_service.model_name

    if hasattr(client, "responses") and hasattr(client.responses, "create"):
        resp = client.responses.create(model=model_name, input=prompt)
        answer = getattr(resp, "output_text", str(resp)).strip()
    elif hasattr(client, "chat") and hasattr(client.chat, "completions"):
        resp = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        answer = (resp.choices[0].message.content or "").strip()
    else:
        answer = "Error calling LLM."

    return {
        "answer": answer,
        "sources_count": len(results),
        "took_ms": int((time.time() - t0) * 1000),
    }


def main():
    parser = argparse.ArgumentParser(description="20-Question Benchmark: Naive RAG vs Agentic RAG")
    parser.add_argument("--top-k", type=int, default=3, help="Top-k chunks per retrieval")
    parser.add_argument("--max-rounds", type=int, default=2, help="Max rounds for agentic RAG")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions to evaluate (for quick test)")
    args = parser.parse_args()

    print("=" * 80)
    print("      20-QUESTION BENCHMARK: NAIVE RAG VS AGENTIC RAG (RFC DATASET)")
    print("=" * 80)

    rag_service = RAGService(
        client=build_llm_client(),
        chunking_service=build_chunking_service(),
        embedding_service=build_embedding_service(),
        vector_db=build_vector_db(),
    )

    agentic_rag = AgenticRAGService(
        rag_service=rag_service,
        top_k=args.top_k,
        max_rounds=args.max_rounds,
        verbose=False,
    )

    questions = BENCHMARK_QUESTIONS[:args.limit] if args.limit else BENCHMARK_QUESTIONS

    naive_scores = []
    agentic_scores = []

    print(f"\n{'ID':<3} | {'Type':<12} | {'Naive RAG':<12} | {'Agentic RAG':<12} | {'Improvement':<12}")
    print("-" * 65)

    for item in questions:
        qid = item["id"]
        qtype = item["type"]
        qtext = item["question"]
        kws = item["keywords"]

        # Run Naive RAG
        naive_out = run_naive_rag(rag_service, qtext, top_k=args.top_k)
        naive_s = score_answer(naive_out["answer"], kws)
        naive_scores.append(naive_s)

        # Run Agentic RAG
        agentic_out = agentic_rag.query(qtext)
        agentic_s = score_answer(agentic_out["answer"], kws)
        agentic_scores.append(agentic_s)

        diff = agentic_s - naive_s
        diff_str = f"+{diff*100:.1f}%" if diff >= 0 else f"{diff*100:.1f}%"
        print(f"{qid:<3} | {qtype:<12} | {naive_s*100:>6.1f}%      | {agentic_s*100:>6.1f}%      | {diff_str:<12}")

    avg_naive = sum(naive_scores) / len(naive_scores)
    avg_agentic = sum(agentic_scores) / len(agentic_scores)
    rel_improvement = ((avg_agentic - avg_naive) / max(0.001, avg_naive)) * 100

    print("=" * 65)
    print(f"Overall Average Naive RAG Score   : {avg_naive*100:.2f}%")
    print(f"Overall Average Agentic RAG Score : {avg_agentic*100:.2f}%")
    print(f"Relative Performance Improvement  : +{rel_improvement:.2f}%")
    print("=" * 65)

    if rel_improvement >= 20.0:
        print("✓ SUCCESS: Agentic RAG achieved >= +20% improvement over Naive RAG!")
    else:
        print(f"Result: {rel_improvement:.1f}% improvement.")


if __name__ == "__main__":
    main()
