"""Query Chroma with all-MiniLM."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR, EMBEDDING_MODEL
from embedding import EmbeddingService
from vectordb import VectorDB


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--persist-dir", type=Path, default=Path(CHROMA_PERSIST_DIR))
    p.add_argument("--collection", default=CHROMA_COLLECTION)
    args = p.parse_args()

    persist_dir = (PROJECT_ROOT / args.persist_dir).resolve() if not args.persist_dir.is_absolute() else args.persist_dir
    db = VectorDB(str(persist_dir), args.collection)
    embedder = EmbeddingService(model_name=EMBEDDING_MODEL)

    qvec = embedder.embed_text(args.query)
    results = db.search(qvec, top_k=args.top_k)

    print(f"collection count: {db.count()}")
    for i, r in enumerate(results, 1):
        d = r["document"]
        print(f"\n[{i}] score={r['score']:.3f} {d['source']}#{d['chunk_id']}")
        print(d["text"][:400])


if __name__ == "__main__":
    main()
