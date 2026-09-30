#!/usr/bin/env python3
"""
Clean Chroma / chunks artifacts – đảm bảo reproducibility khi rebuild.

- Mặc định: xóa collection `rfc_docs` trong `chroma_db/` (giữ file DB)
- --all: xóa toàn bộ thư mục persist (reset hoàn toàn)
- --chunks: xóa luôn data/chunks/*.json (để build lại từ docs)
- --dry-run: chỉ in, không xóa
- --yes: bỏ qua confirm

Ví dụ:
  python scripts/clean_chroma.py --dry-run
  python scripts/clean_chroma.py --collection rfc_docs --yes
  python scripts/clean_chroma.py --all --chunks --yes
  python scripts/clean_chroma.py --chunks --yes   # chỉ xóa chunks
"""

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import CHROMA_COLLECTION, CHROMA_PERSIST_DIR  # type: ignore


def parse_args():
    p = argparse.ArgumentParser(description="Clean Chroma / chunks for reproducibility")
    p.add_argument("--persist-dir", type=Path, default=Path(CHROMA_PERSIST_DIR), help="chroma persist dir (default: chroma_db)")
    p.add_argument("--collection", type=str, default=CHROMA_COLLECTION, help="collection name (default: rfc_docs)")
    p.add_argument("--all", action="store_true", help="xóa toàn bộ persist_dir (reset DB)")
    p.add_argument("--chunks", action="store_true", help="xóa luôn data/chunks/*.json + manifest")
    p.add_argument("--chunks-dir", type=Path, default=PROJECT_ROOT / "data" / "chunks", help="chunks dir")
    p.add_argument("--dry-run", action="store_true", help="chỉ in, không xóa")
    p.add_argument("--yes", action="store_true", help="bỏ qua confirm")
    return p.parse_args()


def confirm(msg: str) -> bool:
    try:
        return input(f"{msg} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def main():
    args = parse_args()
    persist = args.persist_dir if args.persist_dir.is_absolute() else (PROJECT_ROOT / args.persist_dir).resolve()
    chunks_dir = args.chunks_dir if args.chunks_dir.is_absolute() else (PROJECT_ROOT / args.chunks_dir).resolve()

    print(f"[clean] persist_dir={persist}")
    print(f"[clean] collection={args.collection}")
    print(f"[clean] mode={'ALL' if args.all else 'collection-only'} + {'+chunks' if args.chunks else 'keep chunks'}")
    if args.dry_run:
        print("[dry-run] sẽ không xóa gì")

    targets = []

    if args.all:
        if persist.exists():
            targets.append(("persist_dir (ALL)", persist))
        else:
            print(f"  - persist_dir không tồn tại: {persist}")
    else:
        # collection-only: sẽ gọi client.delete_collection, không xóa file DB
        # nhưng vẫn có thể còn segment mồ côi -> in ra để verify
        targets.append(("collection", f"{persist} :: {args.collection}"))

    if args.chunks:
        if chunks_dir.exists():
            # chỉ xóa *.json và manifest, giữ .gitkeep nếu có
            jsons = sorted(chunks_dir.glob("*.json"))
            manifests = sorted(chunks_dir.glob("manifest*.json")) + sorted(chunks_dir.glob("_manifest*.json"))
            for f in jsons + manifests:
                targets.append(("chunks file", f))
            if not jsons:
                print(f"  - chunks_dir rỗng: {chunks_dir}")
        else:
            print(f"  - chunks_dir không tồn tại: {chunks_dir}")

    if not targets:
        print("Không có gì để xóa.")
        return

    print("\nSẽ xóa:")
    for kind, path in targets:
        print(f"  - [{kind}] {path}")

    if not args.dry_run and not args.yes:
        if not confirm("Tiếp tục?"):
            print("Hủy.")
            return

    # --- thực thi ---
    if args.all and not args.dry_run:
        if persist.exists():
            shutil.rmtree(persist)
            print(f"Đã xóa {persist}")

    elif not args.all and not args.dry_run:
        # collection-only via chromadb
        try:
            import chromadb

            client = chromadb.PersistentClient(path=str(persist))
            try:
                client.delete_collection(args.collection)
                print(f"Đã xóa collection '{args.collection}'")
            except Exception as e:
                print(f"Collection '{args.collection}' không tồn tại hoặc lỗi: {e}")
            # dọn segment mồ côi: liệt kê thư mục con không còn trong segments
            # (đơn giản: nếu còn thư mục con không map với segment hiện tại thì xóa)
            try:
                import sqlite3

                db_path = persist / "chroma.sqlite3"
                if db_path.exists():
                    con = sqlite3.connect(str(db_path))
                    cur = con.cursor()
                    cur.execute("SELECT id FROM segments")
                    valid_ids = {row[0] for row in cur.fetchall()}
                    for sub in persist.iterdir():
                        if sub.is_dir() and sub.name not in valid_ids and sub.name != "__pycache__":
                            # chỉ xóa nếu là UUID dir mồ côi và không phải segment hiện tại
                            # an toàn: chỉ xóa khi --yes và thư mục nhỏ (<5M) để tránh xóa nhầm
                            size = sum(f.stat().st_size for f in sub.rglob("*") if f.is_file())
                            if size < 50_000_00:  # 5MB
                                shutil.rmtree(sub)
                                print(f"Đã dọn segment mồ côi {sub.name} ({size//1024}KB)")
                    con.close()
            except Exception as e:
                print(f"[warn] không dọn segment mồ côi được: {e}")
        except ImportError:
            print("[error] chromadb chưa cài, không xóa collection được")
            sys.exit(1)

    if args.chunks and not args.dry_run:
        for kind, path in targets:
            if kind == "chunks file":
                p = Path(path)
                if p.exists():
                    p.unlink()
                    print(f"Đã xóa {p}")

    # summary
    if not args.dry_run:
        # verify
        try:
            import chromadb

            if persist.exists():
                c = chromadb.PersistentClient(path=str(persist))
                try:
                    col = c.get_collection(args.collection)
                    print(f"[verify] collection '{args.collection}' còn {col.count()} docs (nên 0 nếu vừa xóa)")
                except Exception:
                    print(f"[verify] collection '{args.collection}' đã sạch (không tồn tại)")
            else:
                print(f"[verify] persist_dir đã bị xóa")
        except Exception:
            pass
        if args.chunks:
            remaining = list(chunks_dir.glob("*.json")) if chunks_dir.exists() else []
            print(f"[verify] chunks còn lại: {len(remaining)} file")
    print("Done.")


if __name__ == "__main__":
    main()
