"""End-to-End Pipeline Routes: OCR Screenshot Extraction -> PolyRAG Knowledge Retrieval -> Grounded Support Answer."""

import time
from typing import Any, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from OCR.schemas.request_schemas import OCRPredictRequest
from OCR.services.codec.image_codec import ImageCodecError
from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService
from OCR.services.parser.rule_extractor import ExtractedIssue, rule_extractor
from RAG.services.rag_engine import RAGEngine
from server.dependencies import get_ocr_orchestrator, get_rag_engine

pipeline_router = APIRouter(prefix="/api/v1/pipeline", tags=["Pipeline"])


class PipelineDiagnosisResponse(BaseModel):
    """Unified response containing OCR extracted issue, retrieved sources, and generated resolution."""

    answer: str = Field(..., description="Grounded support answer generated from knowledge base.")
    extracted_info: ExtractedIssue = Field(..., description="Structured issue extracted without LLM.")
    sources: list[dict[str, Any]] = Field(default_factory=list, description="Retrieved KB sources and references.")
    pipeline_used: str = Field(default="naive", description="RAG pipeline used: naive, advanced, or agentic.")
    took_ms: int = Field(default=0, description="Total end-to-end execution latency in milliseconds.")
    confidence: float = Field(default=1.0, description="Confidence score of the resolution.")


class PipelineJsonRequest(BaseModel):
    """JSON payload for pipeline diagnosis."""

    image_base64: Optional[str] = Field(None, description="Base64 encoded screenshot image.")
    image_url: Optional[str] = Field(None, description="Remote screenshot image URL.")
    message: Optional[str] = Field(None, description="Optional customer message or query.")
    pipeline: str = Field(default="naive", description="Pipeline mode: naive, advanced, or agentic.")
    top_k: int = Field(default=2, ge=1, le=10, description="Number of knowledge articles to retrieve.")


def _build_search_query(extracted: ExtractedIssue, user_message: Optional[str] = None) -> str:
    """Build a search query from OCR extracted context and optional user message."""
    query_parts = []

    # Priority 1: User message if provided
    if user_message and user_message.strip():
        query_parts.append(user_message.strip())

    # Priority 2: Extracted error codes
    if extracted.error_codes:
        query_parts.append(" ".join(extracted.error_codes))

    # Priority 3: Extracted error message
    if extracted.error_message:
        query_parts.append(extracted.error_message)

    # Priority 4: Extracted details
    if extracted.details:
        query_parts.append(extracted.details)

    # Fallback to raw text if no fields extracted
    if not query_parts and extracted.raw_text:
        query_parts.append(extracted.raw_text[:200])

    return " ".join(query_parts) if query_parts else "General system error"


def _execute_rag(
    rag_engine: RAGEngine,
    query: str,
    pipeline_mode: str,
    top_k: int,
) -> tuple[str, list[dict[str, Any]], float]:
    """Execute the selected PolyRAG pipeline mode."""
    mode = pipeline_mode.lower()
    if mode == "advanced":
        response = rag_engine.query_advanced(question=query, top_k=top_k)
    elif mode == "agentic":
        response = rag_engine.query_agentic(question=query, top_k=top_k)
    else:
        response = rag_engine.query_naive(question=query, top_k=top_k)

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
    ocr_orchestrator: OCROrchestratorService = Depends(get_ocr_orchestrator),
    rag_engine: RAGEngine = Depends(get_rag_engine),
) -> PipelineDiagnosisResponse:
    """
    Full End-to-End Pipeline:
    1. Receives uploaded screenshot image file.
    2. Runs PaddleOCR to extract text.
    3. Runs deterministic rule-based extractor to get structured error info (NO LLM).
    4. Constructs retrieval query from extracted context and user message.
    5. Retrieves matching knowledge from PolyRAG vector database.
    6. Generates grounded support troubleshooting response using LLM.
    """
    start_time = time.time()
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

        # Step 1: OCR Extraction
        ocr_result = ocr_orchestrator.process_image(
            payload=image_bytes,
            is_url=False,
            min_confidence=0.4,
            sort_reading_order=True,
        )

        # Step 2: Rule-Based Extraction (NO LLM)
        line_texts = [item.text for item in ocr_result.lines]
        extracted = rule_extractor.extract(full_text=ocr_result.full_text, lines=line_texts)

        # Step 3: Query PolyRAG
        search_query = _build_search_query(extracted, message)
        answer, sources, confidence = _execute_rag(
            rag_engine=rag_engine,
            query=f"Troubleshoot customer error: {search_query}",
            pipeline_mode=pipeline,
            top_k=top_k,
        )

        total_ms = int((time.time() - start_time) * 1000)

        return PipelineDiagnosisResponse(
            answer=answer,
            extracted_info=extracted,
            sources=sources,
            pipeline_used=pipeline,
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


@pipeline_router.post("/diagnose-json", response_model=PipelineDiagnosisResponse)
def diagnose_json_screenshot(
    request: PipelineJsonRequest,
    ocr_orchestrator: OCROrchestratorService = Depends(get_ocr_orchestrator),
    rag_engine: RAGEngine = Depends(get_rag_engine),
) -> PipelineDiagnosisResponse:
    """Full End-to-End Pipeline on Base64 string or remote image URL."""
    start_time = time.time()
    try:
        payload = request.image_url if request.image_url else request.image_base64
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'image_base64' or 'image_url' must be provided.",
            )

        # Step 1: OCR Extraction
        ocr_result = ocr_orchestrator.process_image(
            payload=payload,
            is_url=bool(request.image_url),
            min_confidence=0.4,
            sort_reading_order=True,
        )

        # Step 2: Rule-Based Extraction
        line_texts = [item.text for item in ocr_result.lines]
        extracted = rule_extractor.extract(full_text=ocr_result.full_text, lines=line_texts)

        # Step 3: Query PolyRAG
        search_query = _build_search_query(extracted, request.message)
        answer, sources, confidence = _execute_rag(
            rag_engine=rag_engine,
            query=f"Troubleshoot customer error: {search_query}",
            pipeline_mode=request.pipeline,
            top_k=request.top_k,
        )

        total_ms = int((time.time() - start_time) * 1000)

        return PipelineDiagnosisResponse(
            answer=answer,
            extracted_info=extracted,
            sources=sources,
            pipeline_used=request.pipeline,
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
