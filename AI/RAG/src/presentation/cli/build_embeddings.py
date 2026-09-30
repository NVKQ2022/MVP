"""CLI tool to build embeddings from pre-chunked JSON data."""

import argparse
import json
from pathlib import Path

from src.container import default_container


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]

    p = argparse.ArgumentParser(description="Build Chroma vector store from chunks")
    p.add_argument(
        "--input-file",
        type=Path,
        default=project_root / "data" / "chunks" / "chunks.json",
        help="Path to chunks.json",
    )
    p.add_argument("--batch-size", type=int, default=128, help="Batch size for embedding")
    p.add_argument("--clear", action="store_true", help="Clear store before adding")
    args = p.parse_args()

    input_file = args.input_file if args.input_file.is_absolute() else (project_root / args.input_file).resolve()
    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        return

    documents = json.loads(input_file.read_text(encoding="utf-8"))
    print(f"Loaded {len(documents)} chunks from {input_file}")

    vector_store = default_container.build_vector_store()
    embedding_model = default_container.build_embedding_model()

    if args.clear:
        print("Clearing vector store...")
        vector_store.clear()

    print("Computing embeddings and indexing...")
    texts = [d["text"] for d in documents]
    vectors = embedding_model.embed_batch(texts, batch_size=args.batch_size)

    vector_store.add_documents(vectors=vectors, documents=documents)
    print(f"Indexing complete! Collection count: {vector_store.count()}")


if __name__ == "__main__":
    main()
