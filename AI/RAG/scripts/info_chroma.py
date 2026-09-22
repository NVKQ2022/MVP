#!/usr/bin/env python3
"""
Inspect and display information about the Chroma vector store.

Usage:
    python scripts/info_chroma.py
    python scripts/info_chroma.py --collection rfc_docs
    python scripts/info_chroma.py --json
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR
from vectordb import VectorDB


def get_dir_size_str(path: Path) -> str:
    """Calculate directory size in human-readable format."""
    if not path.exists():
        return "0 B"
    total_bytes = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    for unit in ["B", "KB", "MB", "GB"]:
        if total_bytes < 1024.0:
            return f"{total_bytes:.1f} {unit}"
        total_bytes /= 1024.0
    return f"{total_bytes:.1f} TB"


def get_chroma_info(persist_dir: Path, collection_name: str, sample_limit: int = 2) -> dict:
    """Retrieve metadata and stats from ChromaDB."""
    db = VectorDB(persist_directory=str(persist_dir), collection_name=collection_name)
    col = db.collection

    total_count = db.count()

    # Determine embedding dimension
    sample_doc = col.get(limit=1, include=["embeddings", "metadatas", "documents"])
    embeddings = sample_doc.get("embeddings")
    embedding_dim = len(embeddings[0]) if embeddings is not None and len(embeddings) > 0 else None

    # Distance metric from collection metadata
    distance_metric = col.metadata.get("hnsw:space", "l2") if col.metadata else "unknown"

    # Count chunks per source
    source_counts = Counter()
    if total_count > 0:
        metas = col.get(include=["metadatas"]).get("metadatas", [])
        for m in metas:
            if m:
                source_counts[m.get("source", "unknown")] += 1

    # Fetch sample records
    peek = db.peek(limit=sample_limit)
    samples = []
    if peek and peek.get("ids"):
        for i in range(len(peek["ids"])):
            samples.append({
                "id": peek["ids"][i],
                "metadata": peek["metadatas"][i] if peek.get("metadatas") else {},
                "text_snippet": (peek["documents"][i][:120] + "...") if peek.get("documents") else "",
            })

    return {
        "persist_dir": str(persist_dir),
        "disk_size": get_dir_size_str(persist_dir),
        "collection_name": collection_name,
        "total_chunks": total_count,
        "embedding_dim": embedding_dim,
        "distance_metric": distance_metric,
        "source_counts": dict(sorted(source_counts.items())),
        "samples": samples,
    }


def print_formatted_info(info: dict):
    """Print the information in a clean, human-readable terminal format."""
    print("=" * 65)
    print("               CHROMA STORE INFORMATION")
    print("=" * 65)
    print(f"Persist Directory : {info['persist_dir']} ({info['disk_size']})")
    print(f"Collection Name   : {info['collection_name']}")
    print(f"Distance Metric   : {info['distance_metric']}")
    print(f"Embedding Dim     : {info['embedding_dim'] or 'Not stored / empty'}")
    print(f"Total Chunks      : {info['total_chunks']}")
    print("-" * 65)

    print("Chunks per Document Source:")
    if info["source_counts"]:
        for src, cnt in info["source_counts"].items():
            print(f"  • {src:<20} : {cnt:>5} chunks")
    else:
        print("  (Collection is empty)")

    print("-" * 65)
    print(f"Sample Records (first {len(info['samples'])}):")
    for s in info["samples"]:
        print(f"  ID       : {s['id']}")
        print(f"  Metadata : {s['metadata']}")
        print(f"  Preview  : {s['text_snippet']!r}")
        print()
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Inspect Chroma DB collection details and statistics.")
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=Path(CHROMA_PERSIST_DIR),
        help=f"Directory where Chroma is persisted (default: {CHROMA_PERSIST_DIR})",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=CHROMA_COLLECTION,
        help=f"Collection name to inspect (default: {CHROMA_COLLECTION})",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=2,
        help="Number of sample chunks to display (default: 2)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text",
    )
    args = parser.parse_args()

    persist_dir = (PROJECT_ROOT / args.persist_dir).resolve() if not args.persist_dir.is_absolute() else args.persist_dir

    info = get_chroma_info(
        persist_dir=persist_dir,
        collection_name=args.collection,
        sample_limit=args.samples,
    )

    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print_formatted_info(info)


if __name__ == "__main__":
    main()
