#!/usr/bin/env python3
"""Clean Chroma / chunks artifacts - ensures reproducibility."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.presentation.cli.clean_chroma import main, parse_args

if __name__ == "__main__":
    main()
