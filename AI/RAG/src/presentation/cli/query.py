"""CLI tool to run semantic vector search."""

import argparse
from pathlib import Path

from src.container import default_container


def main() -> None:
    p = argparse.ArgumentParser(description="Query Chroma vector store with embeddings")
    p.add_argument("--query", required=True, help="Search query")
    p.add_argument("--top-k", type=int, default=5, help="Number of results")
    args = p.parse_args()

    vector_store = default_container.build_vector_store()
    embedding_model = default_container.build_embedding_model()

    qvec = embedding_model.embed_text(args.query)
    results = vector_store.search(qvec, top_k=args.top_k)

    print(f"Collection Count: {vector_store.count()}")
    for i, r in enumerate(results, 1):
        doc = r.get("document", {})
        print(f"\n[{i}] score={r.get('score', 0):.3f} {doc.get('source')}#{doc.get('chunk_id')}")
        print(doc.get("text", "")[:400])


if __name__ == "__main__":
    main()
