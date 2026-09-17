"""
Build chunks from data/docs/*.txt using chunking.chunk_text

Reads all .txt files in data/docs, splits each with chunk_text(),
and writes results to data/chunks/.

Output:
  - data/chunks/chunks.json   (combined list, default)
  - data/chunks/<doc>.json    (per-document, if --per-file)

Usage:
  python scripts/build_chunks.py
  python scripts/build_chunks.py --chunk-size 500 --overlap 50
  python scripts/build_chunks.py --per-file
  python -m scripts.build_chunks --help
"""
import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve project root & make `chunking` importable regardless of cwd
# ---------------------------------------------------------------------------
# scripts/build_chunks.py -> parents[1] == project root (RAG/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from chunking import chunk_text  # type: ignore
except ImportError as e:
    raise ImportError(
        f"Cannot import chunk_text from chunking.py at {PROJECT_ROOT / 'chunking.py'}: {e}"
    ) from e


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build chunks from data/docs txt files")
    p.add_argument(
        "--input-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "docs",
        help="Directory containing .txt source files (default: data/docs)",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "chunks",
        help="Directory to write chunks (default: data/chunks)",
    )
    p.add_argument(
        "--output-file",
        type=Path,
        default=None,
        help="Combined JSON filename (default: <output-dir>/chunks.json). "
        "If relative, resolved against --output-dir.",
    )
    p.add_argument("--chunk-size", type=int, default=300, help="chunk_size for chunk_text (default: 300)")
    p.add_argument("--overlap", type=int, default=30, help="overlap for chunk_text (default: 30)")
    p.add_argument(
        "--per-file",
        action="store_true",
        help="Also write one JSON per source file (<output-dir>/<stem>.json)",
    )
    p.add_argument(
        "--no-combined",
        action="store_true",
        help="Do not write combined chunks.json (only per-file when --per-file is set)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    input_dir: Path = args.input_dir
    output_dir: Path = args.output_dir

    # Resolve output_file relative to output_dir if not absolute
    if args.output_file is None:
        output_file = output_dir / "chunks.json"
    else:
        output_file = args.output_file
        if not output_file.is_absolute():
            # if user passed just a filename, put it in output_dir
            # if they passed a relative path like data/chunks.json, resolve against PROJECT_ROOT
            if output_file.parent == Path("."):
                output_file = output_dir / output_file
            else:
                output_file = (PROJECT_ROOT / output_file).resolve()

    if not input_dir.exists():
        print(f"[error] input dir not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    txt_files = sorted(input_dir.glob("*.txt"))
    if not txt_files:
        print(f"[warn] no *.txt files found in {input_dir}", file=sys.stderr)

    output_dir.mkdir(parents=True, exist_ok=True)
    # also ensure parent of combined file exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    all_chunks: list[dict] = []
    per_file_counts: dict[str, int] = {}

    for file_path in txt_files:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text, chunk_size=args.chunk_size, overlap=args.overlap)

        per_file_counts[file_path.name] = len(chunks)

        doc_chunks: list[dict] = []
        for idx, chunk in enumerate(chunks):
            record = {
                "source": file_path.name,
                "chunk_id": idx,
                "text": chunk,
            }
            all_chunks.append(record)
            doc_chunks.append(record)

        if args.per_file:
            per_file_path = output_dir / f"{file_path.stem}.json"
            with open(per_file_path, "w", encoding="utf-8") as f:
                json.dump(doc_chunks, f, ensure_ascii=False, indent=2)
            print(f"  {file_path.name}: {len(chunks)} chunks -> {per_file_path.relative_to(PROJECT_ROOT)}")

    if not args.no_combined:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    # Summary
    try:
        rel_out = output_file.relative_to(PROJECT_ROOT)
    except ValueError:
        rel_out = output_file
    print(f"\nDone. {len(txt_files)} files -> {len(all_chunks)} total chunks")
    if not args.no_combined:
        print(f"Combined: {rel_out} ({len(all_chunks)} chunks)")
    for name, cnt in per_file_counts.items():
        print(f"  - {name}: {cnt}")


if __name__ == "__main__":
    main()
