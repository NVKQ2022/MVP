# startAgenticRag.py

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import (
    build_vector_db,
    build_embedding_service,
    build_llm_client,
    build_chunking_service,
)
from rag_service import RAGService
from agenticRag import AgenticRAGService


def main():
    parser = argparse.ArgumentParser(description="Run Agentic RAG with observable action logging.")
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

    print("Initializing RAG Service and Vector Database...")
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
        verbose=True,
    )

    result = agentic_rag.query(args.query)

    print("\n" + "=" * 70)
    print("                      FINAL ANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\n" + "=" * 70)
    print("                     AGENT SUMMARY")
    print("=" * 70)
    print(f"Total Latency     : {result.get('took_ms')} ms")
    print(f"Reasoning Summary : {result.get('reasoning_summary')}")
    print(f"Confidence Score  : {result.get('confidence')}")
    print(f"Sources Used ({len(result.get('sources', []))}):")
    for src in result.get("sources", []):
        print(f"  • {src.get('source')}#chunk_{src.get('chunk_id')}")

    print("\n" + "=" * 70)
    print("               COMPLETE ACTION TRAJECTORY LOG")
    print("=" * 70)
    for idx, log in enumerate(result.get("agent_log", []), start=1):
        action = log.get("action", "UNKNOWN")
        took = f"({log.get('took_ms')}ms)" if "took_ms" in log else ""
        print(f"\n[{idx}] ACTION: {action} {took}")
        for key, val in log.items():
            if key not in ("action", "took_ms"):
                print(f"    - {key}: {val}")


if __name__ == "__main__":
    main()