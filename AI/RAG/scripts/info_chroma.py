#!/usr/bin/env python3
"""Inspect and display information about the Chroma vector store."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vectordb import ChromaVectorDB
from src.presentation.cli.info_chroma import get_chroma_info, print_formatted_info, main

if __name__ == "__main__":
    main()
