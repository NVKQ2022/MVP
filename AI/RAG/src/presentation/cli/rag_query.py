"""CLI tool to execute Naive RAG (Retrieve and Generate)."""

import argparse

from src.container import default_container


def main() -> None:
    p = argparse.ArgumentParser(description="Query Naive RAG system")
    p.add_argument("--query", required=True, help="Question to ask")
    p.add_argument("--top-k", type=int, default=5, help="Top-K context chunks")
    args = p.parse_args()

    naive_rag = default_container.build_naive_rag()
    resp = naive_rag.execute(args.query, top_k=args.top_k)

    print(f"Retrieved {len(resp.sources)} chunks in {resp.took_ms} ms")
    print("\nAnswer:")
    print(resp.answer)


if __name__ == "__main__":
    main()
