#!/usr/bin/env python3
"""
Create a clean, ready-to-run ZIP archive of ChatbotOCR.
Excludes virtual environments, git history, python byte-code, and temporary files.
Copies the resulting archive to both the parent directory and Windows Downloads.
"""

import os
import shutil
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PARENT_DIR = ROOT_DIR.parent
ZIP_NAME = "ChatbotOCR.zip"
TARGET_ZIP = PARENT_DIR / ZIP_NAME
WIN_DOWNLOADS_ZIP = Path("/mnt/c/Users/quan/Downloads") / ZIP_NAME

EXCLUDE_DIRS = {"venv", ".venv", ".git", ".pytest_cache", "__pycache__"}
EXCLUDE_EXTS = {".pyc", ".pyo"}
EXCLUDE_FILES = {"REQUIREMENT.md"}

def create_project_zip() -> None:
    print(f"📦 Packaging '{ROOT_DIR.name}' from {ROOT_DIR}...")
    
    file_count = 0
    with zipfile.ZipFile(TARGET_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(ROOT_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in sorted(files):
                file_path = Path(root) / file
                if (
                    file in EXCLUDE_FILES
                    or file.startswith("~$")
                    or file == ".DS_Store"
                    or file_path.suffix in EXCLUDE_EXTS
                ):
                    continue
                arcname = Path("ChatbotOCR") / file_path.relative_to(ROOT_DIR)
                zipf.write(file_path, arcname)
                file_count += 1

    size_mb = TARGET_ZIP.stat().st_size / (1024 * 1024)
    print(f"✅ Archive created: {TARGET_ZIP} ({size_mb:.2f} MB, {file_count} files)")

    if WIN_DOWNLOADS_ZIP.parent.exists():
        shutil.copy(TARGET_ZIP, WIN_DOWNLOADS_ZIP)
        print(f"📂 Copied to Windows Downloads: {WIN_DOWNLOADS_ZIP}")

if __name__ == "__main__":
    create_project_zip()
