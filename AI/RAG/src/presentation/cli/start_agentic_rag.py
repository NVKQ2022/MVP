"""CLI Runner for Agentic RAG."""

import argparse
import sys
from pathlib import Path

from src.container import default_container


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Agentic RAG with observable action trajectory logging.")
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default="When a DNS response exceeds the UDP size limit in RFC 1035, which header bit is set, and what TCP flags defined in RFC 793 are sent to initiate the fallback connection?",
        help="Question to ask the Agentic RAG system",
    )
    parser.add_argument("--top-k", type=int, default=3, help="Top-K chunks per retrieval round")
    parser.add_argument("--max-rounds", type=int, default=3, help="Maximum retrieval rounds")
    args = parser.parse_args()

    print("Initializing Agentic RAG Service via Clean Architecture Container...")
    agentic_rag = default_container.build_agentic_rag(
        top_k=args.top_k,
        max_rounds=args.max_rounds,
        verbose=True,
    )

    result = agentic_rag.execute(args.query)

    print("\n" + "=" * 70)
    print("                      FINAL ANSWER")
    print("=" * 70)
    print(result.answer)

    print("\n" + "=" * 70)
    print("                     AGENT SUMMARY")
    print("=" * 70)
    print(f"Total Latency     : {result.took_ms} ms")
    print(f"Reasoning Summary : {result.reasoning_summary}")
    print(f"Confidence Score  : {result.confidence}")
    print(f"Sources Used ({len(result.sources)}):")
    for src in result.sources:
        print(f"  • {src.get('source')}#chunk_{src.get('chunk_id')}")

    print("\n" + "=" * 70)
    print("               COMPLETE ACTION TRAJECTORY LOG")
    print("=" * 70)
    for idx, log in enumerate(result.agent_log, start=1):
        action = log.get("action", "UNKNOWN")
        took = f"({log.get('took_ms')}ms)" if "took_ms" in log else ""
        print(f"\n[{idx}] ACTION: {action} {took}")
        for key, val in log.items():
            if key not in ("action", "took_ms"):
                print(f"    - {key}: {val}")


if __name__ == "__main__":
    main()
