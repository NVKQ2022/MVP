"""Build a Chroma collection from pre-chunked JSON data.

The input JSON must contain documents with at least:

    {
        "text": "...",
        "source": "...",
        "chunk_id": 0
    }

Run:
    python scripts/build_chroma.py

Examples:
    python scripts/build_chroma.py --clear
    python scripts/build_chroma.py --limit 1000
    python scripts/build_chroma.py --batch-size 128
    python scripts/build_chroma.py \
        --persist-dir data/chroma \
        --collection rfc_docs
"""

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Project path
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Application imports
# ---------------------------------------------------------------------------

from config import (
    CHROMA_COLLECTION,
    CHROMA_PERSIST_DIR,
)

from main import (
    build_embedding_service,
    build_vector_db,
)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Chroma vector collection from pre-chunked data."
    )

    parser.add_argument(
        "--chunks",
        type=Path,
        default=PROJECT_ROOT / "data/chunks/chunks.json",
        help="Path to chunks.json",
    )

    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=Path(CHROMA_PERSIST_DIR),
        help="Chroma persistence directory",
    )

    parser.add_argument(
        "--collection",
        type=str,
        default=CHROMA_COLLECTION,
        help="Chroma collection name",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N chunks",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=128,
        help="Embedding batch size",
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the collection before inserting documents",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_path(path: Path) -> Path:
    """Resolve relative paths against the project root."""

    if path.is_absolute():
        return path

    return (PROJECT_ROOT / path).resolve()


def load_chunks(path: Path, limit: int | None) -> list[dict]:
    """Load pre-chunked documents from JSON."""

    if not path.exists():
        print(
            f"[error] chunks not found: {path}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        chunks = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        print(
            f"[error] invalid JSON in {path}: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not isinstance(chunks, list):
        print(
            "[error] chunks.json must contain a JSON array",
            file=sys.stderr,
        )
        sys.exit(1)

    if limit is not None:
        if limit < 0:
            print(
                "[error] --limit must be >= 0",
                file=sys.stderr,
            )
            sys.exit(1)

        chunks = chunks[:limit]

    return chunks


def validate_chunks(chunks: list[dict]) -> None:
    """Validate the minimum document structure required by VectorDB."""

    required_fields = {
        "text",
        "source",
        "chunk_id",
    }

    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            raise ValueError(
                f"chunk at index {index} is not an object"
            )

        missing_fields = required_fields - chunk.keys()

        if missing_fields:
            raise ValueError(
                f"chunk at index {index} is missing fields: "
                f"{sorted(missing_fields)}"
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    if args.batch_size <= 0:
        raise ValueError(
            "--batch-size must be greater than 0"
        )

    chunks_path = resolve_path(args.chunks)
    persist_dir = resolve_path(args.persist_dir)

    # -----------------------------------------------------------------------
    # Load chunks
    # -----------------------------------------------------------------------

    chunks = load_chunks(
        chunks_path,
        args.limit,
    )

    validate_chunks(chunks)

    if not chunks:
        print("[warning] no chunks to process")
        return

    print(
        f"[build] {len(chunks)} chunks "
        f"-> {persist_dir} [{args.collection}]"
    )

    # -----------------------------------------------------------------------
    # Build embedding service
    # -----------------------------------------------------------------------

    embedding_service = build_embedding_service()

    print(
        "[build] embedding "
        f"dim={embedding_service.dim}"
    )

    # -----------------------------------------------------------------------
    # Generate embeddings
    # -----------------------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        f"[build] generating embeddings "
        f"batch_size={args.batch_size}"
    )

    vectors = embedding_service.embed_batch(
        texts,
        batch_size=args.batch_size,
    )

    if len(vectors) != len(chunks):
        raise RuntimeError(
            "Number of embeddings does not match "
            "number of chunks"
        )

    print(
        f"[build] embedded {len(vectors)} vectors"
    )

    # -----------------------------------------------------------------------
    # Build vector database
    # -----------------------------------------------------------------------

    vector_db = build_vector_db(
        persist_directory=str(persist_dir),
        collection_name=args.collection,
    )

    if args.clear:
        print("[build] clearing collection...")
        vector_db.clear()

    print(
        f"[build] count before: "
        f"{vector_db.count()}"
    )

    # -----------------------------------------------------------------------
    # Store documents + vectors
    # -----------------------------------------------------------------------

    vector_db.add_documents(
        vectors=vectors,
        documents=chunks,
    )

    print(
        f"[build] count after: "
        f"{vector_db.count()}"
    )

    print("[build] done.")


if __name__ == "__main__":
    main()
