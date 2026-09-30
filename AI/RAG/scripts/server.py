"""RAG Server - delegates to Clean Architecture FastAPI presentation layer."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.presentation.api.app import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Development reload")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "scripts.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
