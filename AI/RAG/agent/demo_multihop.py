"""
agent/demo_multihop.py - Multi-hop retrieval demonstration with step-by-step logs.

Usage:
    python agent/demo_multihop.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from main import build_llm_client, build_embedding_service, build_vector_db
from config import MODEL_NAME
from agent.react_agent import ReActAgent


def run_demo():
    print("=" * 75)
    print("            REACT AGENTIC RAG: MULTI-HOP DEMONSTRATION")
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

    # Multi-hop question:
    # 1. Hop 1: What protocol does HTTP/3 use? -> QUIC (RFC 9000 / RFC 9110)
    # 2. Hop 2: How does QUIC handle connection migration? -> Connection IDs (RFC 9000)
    question = (
        "What underlying transport protocol does HTTP/3 rely on, "
        "and how does that transport protocol handle connection migration across client IP address changes?"
    )

    print(f"\n[QUESTION]:\n{question}\n")
    print("-" * 75)

    response = agent.query(question=question, top_k=3, max_steps=4)

    print("\n[AGENT OBSERVABLE TRAJECTORY (Thought -> Action -> Observation)]")
    for step in response.trajectory:
        print(f"\n>> [Step {step.step_num}] [Action: {step.action}]")
        print(f"   Thought: {step.thought}")
        print(f"   Input:   {step.action_input}")
        if step.chunks_retrieved > 0:
            print(f"   Observation: Retrieved {step.chunks_retrieved} new chunks.")
        else:
            print(f"   Observation: {step.observation[:200]}...")

    print("\n" + "=" * 75)
    print("[FINAL GROUNDED SYNTHESIS WITH CITATIONS]")
    print("=" * 75)
    print(response.answer)

    print("\n[SOURCES CITED]")
    for s in response.sources:
        print(f"  • {s['source']}#{s['chunk_id']} (Score: {s['score']}) [Step {s['round']}]")

    print(f"\nStats: {response.took_ms} ms | {response.total_steps} Steps | Confidence: {response.confidence:.2f}")


if __name__ == "__main__":
    run_demo()
