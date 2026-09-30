"""FastAPI application factory and route definitions."""

from pathlib import Path
import time
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.container import Container, default_container
from src.presentation.api.schemas import AgenticQueryRequest, HealthResponse, QueryRequest


def create_app(container: Container | None = None) -> FastAPI:
    """Create and configure FastAPI application instance."""
    app_container = container or default_container

    from contextlib import asynccontextmanager

    # Lazy-loaded runtime use cases
    state: dict[str, Any] = {
        "naive_rag": None,
        "agentic_rag": None,
        "llm_available": False,
    }

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            naive_rag = app_container.build_naive_rag()
            state["naive_rag"] = naive_rag
            state["llm_available"] = naive_rag.llm_client is not None

            if state["llm_available"]:
                state["agentic_rag"] = app_container.build_agentic_rag(
                    naive_rag=naive_rag,
                    verbose=False,
                )
        except Exception as e:
            print(f"[API] Error during startup initialization: {e}")
        yield

    app = FastAPI(
        title="RFC Agentic RAG API",
        version="2.0.0",
        description="Clean Architecture RAG & Agentic RAG Web API for Technical RFC Specifications",
        lifespan=lifespan,
    )

    project_root = Path(__file__).resolve().parents[3]
    static_dir = project_root / "static"

    if static_dir.exists():
        app.mount(
            "/static",
            StaticFiles(directory=str(static_dir)),
            name="static",
        )

    @app.get("/health")
    def health() -> dict[str, Any]:
        naive = state.get("naive_rag")
        if naive is None:
            return {"status": "starting", "llm_available": False}

        return {
            "status": "ok",
            "embedding_dim": naive.embedding_model.dim,
            "vector_collection": naive.vector_store.collection_name
            if hasattr(naive.vector_store, "collection_name")
            else "unknown",
            "vector_count": naive.vector_store.count(),
            "llm_model": naive.llm_client.model_name if naive.llm_client else None,
            "llm_available": state["llm_available"],
        }

    @app.get("/")
    def root():
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))

        return {
            "message": "RFC Agentic RAG API Server",
            "docs": "/docs",
            "health": "/health",
            "frontend": "/static/index.html",
        }

    @app.post("/query")
    def query(req: QueryRequest) -> dict[str, Any]:
        naive = state.get("naive_rag")
        if naive is None:
            return {"error": "RAG service is not initialized"}

        t0 = time.time()
        results = naive.retrieve(query=req.query, top_k=req.top_k)
        took_ms = int((time.time() - t0) * 1000)

        return {
            "query": req.query,
            "top_k": req.top_k,
            "took_ms": took_ms,
            "results": [
                {
                    "score": r.get("score", 0.0),
                    "distance": r.get("distance", 0.0),
                    "source": r.get("document", {}).get("source"),
                    "chunk_id": r.get("document", {}).get("chunk_id"),
                    "text": r.get("document", {}).get("text"),
                }
                for r in results
            ],
        }

    @app.post("/rag")
    def rag(req: QueryRequest) -> dict[str, Any]:
        naive = state.get("naive_rag")
        if naive is None:
            return {"error": "RAG service is not initialized"}

        response = naive.execute(question=req.query, top_k=req.top_k)
        return response.to_dict()

    @app.post("/agentic-rag")
    def agentic_rag(req: AgenticQueryRequest) -> dict[str, Any]:
        agentic = state.get("agentic_rag")
        if agentic is None:
            return {"error": "Agentic RAG is not initialized (check LLM configuration)"}

        # Override params for request
        agentic.top_k = req.top_k
        agentic.max_rounds = req.max_rounds

        response = agentic.execute(question=req.query)
        return response.to_dict()

    return app


# Default app instance
app = create_app()
