"""Build Chroma collection from data/chunks/chunks.json using all-MiniLM."""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR, EMBEDDING_MODEL
from embedding import EmbeddingService
from vectordb import VectorDB



def parse_args():
    p = argparse.ArgumentParser(description="Build Chroma with all-MiniLM")
    p.add_argument("--chunks", type=Path, default=PROJECT_ROOT / "data/chunks/chunks.json")
    p.add_argument("--persist-dir", type=Path, default=Path(CHROMA_PERSIST_DIR))
    p.add_argument("--collection", type=str, default=CHROMA_COLLECTION)
    p.add_argument("--limit", type=int, default=None, help="only first N chunks")
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--clear", action="store_true", help="clear collection first")
    return p.parse_args()


def main():
    args = parse_args()
    persist_dir = (PROJECT_ROOT / args.persist_dir).resolve() if not args.persist_dir.is_absolute() else args.persist_dir

    chunks_path = args.chunks
    if not chunks_path.exists():
        print(f"[error] chunks not found: {chunks_path} (expected data/chunks/chunks.json)", file=sys.stderr)
        sys.exit(1)
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    if args.limit:
        chunks = chunks[: args.limit]

    print(f"{len(chunks)} chunks -> {persist_dir} [{args.collection}]")

    embedder = EmbeddingService(model_name=EMBEDDING_MODEL)
    print(f"embedding with {embedder.model_name} (dim={embedder.dim})")
    texts = [c["text"] for c in chunks]
    vectors = embedder.embed_batch(texts, batch_size=args.batch_size)
    print(f"embedded {len(vectors)} vectors")

    db = VectorDB(str(persist_dir), args.collection)
    if args.clear:
        db.clear()
    print(f"count before: {db.count()}")
    db.add_documents(vectors, chunks)
    print(f"count after: {db.count()}")
    print("done.")


if __name__ == "__main__":
    main()
