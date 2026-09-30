"""CLI Tool to clean Chroma artifacts."""

import argparse
from pathlib import Path
import shutil

from src.infrastructure.config.settings import CHROMA_COLLECTION, CHROMA_PERSIST_DIR


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Clean Chroma / chunks for reproducibility")
    p.add_argument("--persist-dir", type=Path, default=Path(CHROMA_PERSIST_DIR), help="chroma persist dir")
    p.add_argument("--collection", type=str, default=CHROMA_COLLECTION, help="collection name")
    p.add_argument("--all", action="store_true", help="delete entire persist_dir")
    p.add_argument("--chunks", action="store_true", help="delete data/chunks/*.json")
    p.add_argument("--dry-run", action="store_true", help="preview only")
    p.add_argument("--yes", action="store_true", help="skip confirmation")
    return p.parse_args()


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    args = parse_args()
    persist = (project_root / args.persist_dir).resolve() if not args.persist_dir.is_absolute() else args.persist_dir
    chunks_dir = project_root / "data" / "chunks"

    print(f"[clean] persist_dir={persist}")
    print(f"[clean] collection={args.collection}")

    if args.dry_run:
        print("[clean] DRY RUN - no files deleted")
        return

    if not args.yes:
        confirm = input("Are you sure you want to proceed with deletion? [y/N] ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Aborted.")
            return

    if args.all and persist.exists():
        shutil.rmtree(persist)
        print(f"Deleted persist dir: {persist}")
    elif persist.exists():
        # Clear collection using Chroma
        import chromadb
        client = chromadb.PersistentClient(path=str(persist))
        try:
            client.delete_collection(args.collection)
            print(f"Deleted collection: {args.collection}")
        except Exception as e:
            print(f"Collection deletion notice: {e}")

    if args.chunks and chunks_dir.exists():
        for json_file in chunks_dir.glob("*.json"):
            json_file.unlink()
            print(f"Deleted chunk file: {json_file}")


if __name__ == "__main__":
    main()
