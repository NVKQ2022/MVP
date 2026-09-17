"""RAG Server - load model once, query fast.

Startup: load all-MiniLM (26s once) + Chroma + LLM client.
After that: /query ~0.05s, /rag ~0.05s + LLM time.

Run:
  python scripts/server.py
  python scripts/server.py --port 8001 --host 0.0.0.0
  uvicorn scripts.server:app --host 0.0.0.0 --port 8000

Test:
  curl http://localhost:8000/health
  curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query":"QUIC handshake","top_k":3}'
  curl -X POST http://localhost:8000/rag -H "Content-Type: application/json" -d '{"query":"What is DNS?","top_k":3}'
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import API_KEY, CHROMA_COLLECTION, CHROMA_PERSIST_DIR, EMBEDDING_MODEL, ENDPOINT, MODEL_NAME

app = FastAPI(title="RAG Server (all-MiniLM + Chroma)", version="1.0")

# serve frontend if exists
STATIC_DIR = PROJECT_ROOT / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# globals - loaded once at startup
embedder = None
db = None
llm_client = None


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class RagRequest(BaseModel):
    query: str
    top_k: int = 5


@app.on_event("startup")
def startup():
    global embedder, db, llm_client
    print("[server] loading embedding model...", flush=True)
    t0 = time.time()
    from embedding import EmbeddingService

    embedder = EmbeddingService(model_name=EMBEDDING_MODEL)
    print(f"[server] embedding {embedder.model_name} dim={embedder.dim} loaded in {time.time()-t0:.1f}s")

    print("[server] loading chroma...", flush=True)
    from vectordb import VectorDB

    # resolve persist_dir
    persist = Path(CHROMA_PERSIST_DIR)
    if not persist.is_absolute():
        persist = (PROJECT_ROOT / persist).resolve()
    db = VectorDB(str(persist), CHROMA_COLLECTION)
    print(f"[server] chroma {CHROMA_COLLECTION}@{persist} count={db.count()}")

    if API_KEY and ENDPOINT and MODEL_NAME:
        print(f"[server] LLM {MODEL_NAME} @ {ENDPOINT}", flush=True)
        from openai import OpenAI

        llm_client = OpenAI(api_key=API_KEY, base_url=ENDPOINT)
    else:
        print("[server] LLM not configured (missing ENDPOINT/API_KEY/MODEL_NAME) - /rag will return context only")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "embedding_model": embedder.model_name if embedder else None,
        "embedding_dim": embedder.dim if embedder else None,
        "chroma_collection": db.collection_name if db else None,
        "chroma_count": db.count() if db else 0,
        "llm_model": MODEL_NAME,
    }


@app.get("/")
def root():
    index = STATIC_DIR / "index.html" if 'STATIC_DIR' in globals() else PROJECT_ROOT / "static" / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "RAG Server ready", "docs": "/docs", "health": "/health", "frontend": "/static/index.html"}


@app.post("/query")
def query(req: QueryRequest):
    t0 = time.time()
    qvec = embedder.embed_text(req.query)
    results = db.search(qvec, top_k=req.top_k)
    return {
        "query": req.query,
        "top_k": req.top_k,
        "took_ms": int((time.time() - t0) * 1000),
        "results": [
            {
                "score": r["score"],
                "distance": r["distance"],
                "source": r["document"].get("source"),
                "chunk_id": r["document"].get("chunk_id"),
                "text": r["document"].get("text"),
            }
            for r in results
        ],
    }


@app.post("/rag")
def rag(req: RagRequest):
    t0 = time.time()
    qvec = embedder.embed_text(req.query)
    results = db.search(qvec, top_k=req.top_k)

    context_blocks = [
        f"Source: {r['document'].get('source')}#{r['document'].get('chunk_id')} (score {r['score']:.3f})\n{r['document'].get('text')}"
        for r in results
    ]
    context = "\n\n---\n\n".join(context_blocks)

    if not llm_client:
        return {
            "query": req.query,
            "answer": None,
            "context": context,
            "sources": [{"source": r["document"].get("source"), "chunk_id": r["document"].get("chunk_id"), "score": r["score"]} for r in results],
            "took_ms": int((time.time() - t0) * 1000),
            "error": "LLM not configured",
        }

    prompt = f"Use the following context to answer. If not in context, say you don't know.\n\nContext:\n{context}\n\nQuestion: {req.query}\nAnswer:"
    resp = llm_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers using provided context."},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=500,
    )
    answer = resp.choices[0].message.content

    return {
        "query": req.query,
        "answer": answer,
        "sources": [{"source": r["document"].get("source"), "chunk_id": r["document"].get("chunk_id"), "score": r["score"]} for r in results],
        "took_ms": int((time.time() - t0) * 1000),
    }


# for `python scripts/server.py`
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="dev reload (will reload model each change - slow)")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run("scripts.server:app", host=args.host, port=args.port, reload=args.reload)
