"""End-to-End Pipeline Routes: OCR Screenshot Extraction -> PolyRAG Knowledge Retrieval -> Support Answer."""

import json
import time
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from OCR.config import settings
from OCR.services.codec.image_codec import ImageCodecError
from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService
from RAG.services.rag_engine import RAGEngine
from server.dependencies import get_ocr_orchestrator, get_rag_engine

pipeline_router = APIRouter(prefix="/api/v1/pipeline", tags=["Pipeline"])


class PipelineDiagnosisResponse(BaseModel):
    """Response containing OCR recognized text, retrieved sources, and generated resolution."""

    answer: str = Field(..., description="Grounded support answer generated from knowledge base.")
    ocr_text: str = Field(..., description="Raw text extracted from the screenshot via OCR.")
    sources: list[dict[str, Any]] = Field(default_factory=list, description="Retrieved KB sources and references.")
    pipeline_used: str = Field(default="naive", description="RAG pipeline used: naive, advanced, or agentic.")
    ocr_version: str = Field(default="PP-OCRv4", description="OCR model architecture used: PP-OCRv4, PP-OCRv3, etc.")
    took_ms: int = Field(default=0, description="Total execution latency in milliseconds.")
    confidence: float = Field(default=1.0, description="Confidence score.")


class PipelineJsonRequest(BaseModel):
    """JSON payload for pipeline diagnosis."""

    image_base64: Optional[str] = Field(None, description="Base64 encoded screenshot image.")
    image_url: Optional[str] = Field(None, description="Remote screenshot image URL.")
    message: Optional[str] = Field(None, description="Optional customer message or query.")
    pipeline: str = Field(default="naive", description="Pipeline mode: naive, advanced, or agentic.")
    ocr_version: Optional[str] = Field(None, description="OCR architecture override: 'PP-OCRv4' (balanced), 'PP-OCRv3' (fastest), or 'PP-OCRv6'")
    top_k: int = Field(default=2, ge=1, le=10, description="Number of knowledge articles to retrieve.")


def _build_rag_prompt(ocr_text: str, user_message: Optional[str] = None) -> str:
    """Build a search/prompt query feeding the OCR text directly into PolyRAG."""
    parts = []
    if user_message and user_message.strip():
        parts.append(f"User Query: {user_message.strip()}")

    clean_ocr = (ocr_text or "").strip()
    if clean_ocr:
        parts.append(f"Screenshot Error Text:\n{clean_ocr}")

    return "\n\n".join(parts) if parts else "Customer encountered a system error."


def _execute_rag(
    rag_engine: RAGEngine,
    prompt: str,
    pipeline_mode: str,
    top_k: int,
) -> tuple[str, list[dict[str, Any]], float]:
    """Execute the selected PolyRAG pipeline mode."""
    mode = pipeline_mode.lower()
    if mode == "advanced":
        response = rag_engine.query_advanced(question=prompt, top_k=top_k)
    elif mode == "agentic":
        response = rag_engine.query_agentic(question=prompt, top_k=top_k)
    else:
        response = rag_engine.query_naive(question=prompt, top_k=top_k)

    sources = []
    for s in response.sources:
        sources.append({
            "id": s.get("article_id") or s.get("source", "KB-DOC"),
            "title": s.get("title", ""),
            "source": s.get("source", ""),
            "chunk_id": s.get("chunk_id", 0),
        })

    return response.answer, sources, response.confidence


@pipeline_router.post("/diagnose", response_model=PipelineDiagnosisResponse)
async def diagnose_uploaded_screenshot(
    file: UploadFile = File(..., description="Screenshot file (PNG, JPG, WEBP)"),
    message: Optional[str] = Form(None, description="Optional customer message or issue description"),
    pipeline: str = Form("naive", description="RAG strategy: 'naive', 'advanced', or 'agentic'"),
    top_k: int = Form(2, ge=1, le=10, description="Number of knowledge articles to retrieve"),
    ocr_version: Optional[str] = Form(None, description="OCR architecture override: 'PP-OCRv4', 'PP-OCRv3', 'PP-OCRv6'"),
    ocr_orchestrator: OCROrchestratorService = Depends(get_ocr_orchestrator),
    rag_engine: RAGEngine = Depends(get_rag_engine),
) -> PipelineDiagnosisResponse:
    """
    Direct Screenshot-to-RAG Pipeline:
    1. Extracts text from the uploaded screenshot via PaddleOCR.
    2. Feeds the OCR text directly into PolyRAG to retrieve matching knowledge.
    3. Generates a grounded resolution using the retrieved context.
    """
    start_time = time.time()
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

        # Step 1: Direct OCR Extraction
        ocr_result = ocr_orchestrator.process_image(
            payload=image_bytes,
            is_url=False,
            min_confidence=0.4,
            sort_reading_order=True,
            ocr_version=ocr_version,
        )

        # Step 2: Feed OCR text directly into PolyRAG
        rag_prompt = _build_rag_prompt(ocr_result.full_text, message)
        answer, sources, confidence = _execute_rag(
            rag_engine=rag_engine,
            prompt=rag_prompt,
            pipeline_mode=pipeline,
            top_k=top_k,
        )

        total_ms = int((time.time() - start_time) * 1000)

        return PipelineDiagnosisResponse(
            answer=answer,
            ocr_text=ocr_result.full_text,
            sources=sources,
            pipeline_used=pipeline,
            ocr_version=ocr_version or settings.ocr_version,
            took_ms=total_ms,
            confidence=confidence,
        )

    except ImageCodecError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline diagnosis failed: {str(e)}",
        )


@pipeline_router.get("/samples")
def get_sample_screenshots() -> list[dict[str, Any]]:
    """Returns available sample screenshots for rapid UI testing."""
    manifest_path = Path("data/sample_screenshots/manifest.json")
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        samples = []
        for item in data:
            samples.append({
                "file": item.get("file"),
                "article_id": item.get("article_id"),
                "variant": item.get("variant"),
                "title": item.get("expected_title"),
                "difficulty": item.get("expected_difficulty"),
                "error_codes": item.get("error_codes", []),
            })
        return samples
    except Exception:
        return []


@pipeline_router.post("/diagnose-json", response_model=PipelineDiagnosisResponse)
def diagnose_json_screenshot(
    request: PipelineJsonRequest,
    ocr_orchestrator: OCROrchestratorService = Depends(get_ocr_orchestrator),
    rag_engine: RAGEngine = Depends(get_rag_engine),
) -> PipelineDiagnosisResponse:
    """Direct Screenshot-to-RAG Pipeline on Base64 string, image URL, or conversational text."""
    start_time = time.time()
    try:
        payload = request.image_url if request.image_url else request.image_base64
        extracted_text = ""

        if payload:
            # Step 1: Direct OCR Extraction
            ocr_result = ocr_orchestrator.process_image(
                payload=payload,
                is_url=bool(request.image_url),
                min_confidence=0.4,
                sort_reading_order=True,
                ocr_version=request.ocr_version,
            )
            extracted_text = ocr_result.full_text
        elif not (request.message and request.message.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either an image ('image_base64' / 'image_url') or a text 'message' must be provided.",
            )

        # Step 2: Feed OCR text / query into PolyRAG
        rag_prompt = _build_rag_prompt(extracted_text, request.message)
        answer, sources, confidence = _execute_rag(
            rag_engine=rag_engine,
            prompt=rag_prompt,
            pipeline_mode=request.pipeline,
            top_k=request.top_k,
        )

        total_ms = int((time.time() - start_time) * 1000)

        return PipelineDiagnosisResponse(
            answer=answer,
            ocr_text=extracted_text,
            sources=sources,
            pipeline_used=request.pipeline,
            ocr_version=request.ocr_version or settings.ocr_version,
            took_ms=total_ms,
            confidence=confidence,
        )

    except ImageCodecError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline diagnosis failed: {str(e)}",
        )
