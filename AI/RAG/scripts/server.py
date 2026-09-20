
"""RAG Server.

Startup:
    Load embedding model + Chroma + LLM client once.

Run:
    python scripts/server.py
    python scripts/server.py --port 8001 --host 0.0.0.0
    uvicorn scripts.server:app --host 0.0.0.0 --port 8000

Test:
    curl http://localhost:8000/health

    curl -X POST http://localhost:8000/query \
        -H "Content-Type: application/json" \
        -d '{"query":"QUIC handshake","top_k":3}'

    curl -X POST http://localhost:8000/rag \
        -H "Content-Type: application/json" \
        -d '{"query":"What is DNS?","top_k":3}'
"""

import argparse
import sys
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Project path
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Application imports
# ---------------------------------------------------------------------------

from config import (
    API_KEY,
    ENDPOINT,
    MODEL_NAME,
)

from main import (
    build_chunking_service,
    build_embedding_service,
    build_llm_client,
    build_vector_db,
)

from rag_service import RAGService


# ---------------------------------------------------------------------------
# FastAPI
# ---------------------------------------------------------------------------

app = FastAPI(
    title="RAG Server",
    version="2.0",
)


# ---------------------------------------------------------------------------
# Static frontend
# ---------------------------------------------------------------------------

STATIC_DIR = PROJECT_ROOT / "static"

if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

rag_service: RAGService | None = None
llm_available = False


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, gt=0)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup() -> None:
    global rag_service
    global llm_available

    print("[server] initializing runtime...", flush=True)

    # -----------------------------------------------------------------------
    # Chunking
    # -----------------------------------------------------------------------

    print("[server] loading chunking service...", flush=True)

    chunking_service = build_chunking_service()

    # -----------------------------------------------------------------------
    # Embedding
    # -----------------------------------------------------------------------

    print("[server] loading embedding service...", flush=True)

    t0 = time.time()

    embedding_service = build_embedding_service()

    embedding_time = time.time() - t0

    print(
        "[server] embedding "
        f"dim={embedding_service.dim} "
        f"loaded in {embedding_time:.1f}s",
        flush=True,
    )

    # -----------------------------------------------------------------------
    # Vector database
    # -----------------------------------------------------------------------

    print("[server] loading vector database...", flush=True)

    vector_db = build_vector_db()

    print(
        "[server] vector database "
        f"collection={vector_db.collection_name} "
        f"count={vector_db.count()}",
        flush=True,
    )

    # -----------------------------------------------------------------------
    # LLM
    # -----------------------------------------------------------------------

    client = None

    if API_KEY and ENDPOINT and MODEL_NAME:
        print(
            f"[server] loading LLM "
            f"{MODEL_NAME} @ {ENDPOINT}",
            flush=True,
        )

        client = build_llm_client()
        llm_available = True

    else:
        print(
            "[server] LLM not configured "
            "(missing ENDPOINT/API_KEY/MODEL_NAME)",
            flush=True,
        )

    # -----------------------------------------------------------------------
    # RAG service
    # -----------------------------------------------------------------------

    rag_service = RAGService(
        client=client,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        vector_db=vector_db,
        model_name=MODEL_NAME,
    )

    print("[server] RAG service ready", flush=True)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    if rag_service is None:
        return {
            "status": "starting",
            "llm_available": False,
        }

    return {
        "status": "ok",
        "embedding_dim": rag_service.embedding_service.dim,
        "vector_collection": rag_service.vector_db.collection_name,
        "vector_count": rag_service.vector_db.count(),
        "llm_model": rag_service.model_name,
        "llm_available": llm_available,
    }


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    index = STATIC_DIR / "index.html"

    if index.exists():
        return FileResponse(str(index))

    return {
        "message": "RAG Server ready",
        "docs": "/docs",
        "health": "/health",
        "frontend": "/static/index.html",
    }


# ---------------------------------------------------------------------------
# Vector search
# ---------------------------------------------------------------------------

@app.post("/query")
def query(req: QueryRequest):
    if rag_service is None:
        return {
            "error": "RAG service is not initialized",
        }

    t0 = time.time()

    results = rag_service.retrieve(
        query=req.query,
        top_k=req.top_k,
    )

    return {
        "query": req.query,
        "top_k": req.top_k,
        "took_ms": int((time.time() - t0) * 1000),
        "results": [
            {
                "score": result["score"],
                "distance": result["distance"],
                "source": result["document"].get("source"),
                "chunk_id": result["document"].get("chunk_id"),
                "text": result["document"].get("text"),
            }
            for result in results
        ],
    }


# ---------------------------------------------------------------------------
# Full RAG
# ---------------------------------------------------------------------------

@app.post("/rag")
def rag(req: QueryRequest):
    if rag_service is None:
        return {
            "error": "RAG service is not initialized",
        }

    t0 = time.time()

    # Always retrieve context first.
    results = rag_service.retrieve(
        query=req.query,
        top_k=req.top_k,
    )

    context = rag_service.format_context(results)

    # Allow retrieval-only mode when no LLM is configured.
    if not llm_available:
        return {
            "query": req.query,
            "answer": None,
            "context": context,
            "sources": [
                {
                    "source": result["document"].get("source"),
                    "chunk_id": result["document"].get("chunk_id"),
                    "score": result["score"],
                }
                for result in results
            ],
            "took_ms": int((time.time() - t0) * 1000),
            "error": "LLM not configured",
        }

    # Full RAG.
    response = rag_service.query(
        question=req.query,
        top_k=req.top_k,
    )

    response["took_ms"] = int(
        (time.time() - t0) * 1000
    )

    return response


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--host",
        default="0.0.0.0",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Development reload. Models may be loaded again after changes.",
    )

    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "scripts.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
