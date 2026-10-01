"""CLI tool for the RAG subsystem powered by PolyRAG."""

import argparse
import sys
from pathlib import Path

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from RAG.services.rag_engine import RAGEngine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query the Support Knowledge Base using PolyRAG.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Question or extracted screenshot error text to ask the knowledge base.",
    )
    parser.add_argument(
        "-p", "--pipeline",
        choices=["naive", "advanced", "agentic"],
        default="naive",
        help="RAG strategy to use: 'naive' (fast 1-shot), 'advanced' (multi-query + RRF fusion), or 'agentic' (iterative reflection).",
    )
    parser.add_argument(
        "-k", "--top-k",
        type=int,
        default=2,
        help="Number of top relevant knowledge chunks to retrieve.",
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Launch an interactive terminal chat session.",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Force re-generation and indexing of knowledge base documents.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed logging and agent reasoning trajectory.",
    )

    args = parser.parse_args()

    print("🔧 Initializing PolyRAG Engine...")
    engine = RAGEngine()

    if args.ingest or engine.vector_store.count() == 0:
        print("📥 Ingesting knowledge documents into ChromaDB...")
        count = engine.ingest_kb_documents(force_regenerate=args.ingest)
        print(f"✅ Ingested {count} chunks. Total indexed: {engine.vector_store.count()}\n")

    def run_query(question: str) -> None:
        print(f"\n🔎 [{args.pipeline.upper()} RAG] Question: {question}")
        print("─" * 60)

        if args.pipeline == "naive":
            res = engine.query_naive(question, top_k=args.top_k)
        elif args.pipeline == "advanced":
            res = engine.query_advanced(question, top_k=args.top_k, verbose=args.verbose)
        elif args.pipeline == "agentic":
            res = engine.query_agentic(question, top_k=args.top_k, verbose=args.verbose)

        print("\n🤖 Answer:")
        print(res.answer)
        print("\n📚 Sources:")
        for s in res.sources:
            src = s.get("source", "N/A")
            cid = s.get("chunk_id", "")
            title = s.get("title", "")
            print(f"  • {src}#{cid} — {title}")
        print(f"⏱ Latency: {res.took_ms}ms | Confidence: {res.confidence}\n")

    if args.interactive or not args.query:
        print("=" * 60)
        print("💬 PolyRAG Interactive Support Terminal (Type 'exit' to quit)")
        print(f"Active Pipeline: {args.pipeline.upper()} | Indexed Chunks: {engine.vector_store.count()}")
        print("=" * 60)
        while True:
            try:
                user_input = input("\nEnter error or question: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit", "q"):
                    print("Goodbye!")
                    break
                run_query(user_input)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                break
    else:
        run_query(args.query)


if __name__ == "__main__":
    main()
