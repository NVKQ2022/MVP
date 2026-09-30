"""CLI tool to build chunks from data/docs/*.txt files."""

import argparse
import json
from pathlib import Path

from src.container import default_container


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]

    p = argparse.ArgumentParser(description="Build chunks from data/docs txt files")
    p.add_argument(
        "--input-dir",
        type=Path,
        default=project_root / "data" / "docs",
        help="Directory containing .txt source files",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "data" / "chunks",
        help="Directory to write chunks",
    )
    p.add_argument(
        "--output-file",
        type=Path,
        default=None,
        help="Combined JSON filename (default: <output-dir>/chunks.json)",
    )
    p.add_argument("--chunk-size", type=int, default=550, help="chunk size")
    p.add_argument("--overlap", type=int, default=35, help="overlap size")
    p.add_argument("--per-file", action="store_true", help="write one JSON per doc")
    args = p.parse_args()

    input_dir = args.input_dir if args.input_dir.is_absolute() else (project_root / args.input_dir).resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else (project_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    chunker = default_container.build_chunker(chunk_size=args.chunk_size, overlap=args.overlap)

    txt_files = sorted(input_dir.glob("*.txt"))
    print(f"Found {len(txt_files)} text files in {input_dir}")

    all_chunks = []
    for txt_file in txt_files:
        text = txt_file.read_text(encoding="utf-8", errors="ignore")
        chunks = chunker.chunk(text)
        file_chunks = []
        for cid, chunk_text in enumerate(chunks):
            doc = {
                "source": txt_file.name,
                "chunk_id": cid,
                "text": chunk_text,
            }
            file_chunks.append(doc)
            all_chunks.append(doc)

        if args.per_file:
            per_path = output_dir / f"{txt_file.stem}.json"
            per_path.write_text(json.dumps(file_chunks, indent=2), encoding="utf-8")
            print(f"Wrote {len(file_chunks)} chunks -> {per_path.name}")

    out_file = args.output_file or (output_dir / "chunks.json")
    out_file.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    print(f"Total chunks: {len(all_chunks)} -> {out_file}")


if __name__ == "__main__":
    main()
