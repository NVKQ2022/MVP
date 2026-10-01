"""Thin FastAPI Controller Routes for OCR Operations."""

from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException, status

from OCR.schemas.request_schemas import OCRPredictRequest
from OCR.schemas.response_schemas import OCRResponse, BackendInfoResponse
from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService
from OCR.services.codec.image_codec import ImageCodecError
from server.dependencies import get_ocr_orchestrator

ocr_router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])


@ocr_router.get("/info", response_model=BackendInfoResponse)
def get_ocr_info(
    orchestrator: OCROrchestratorService = Depends(get_ocr_orchestrator),
) -> BackendInfoResponse:
    """Retrieves active OCR backend information and supported language models."""
    return orchestrator.get_service_info()


@ocr_router.post("/predict", response_model=OCRResponse)
def predict_ocr(
    request: OCRPredictRequest,
    orchestrator: OCROrchestratorService = Depends(get_ocr_orchestrator),
) -> OCRResponse:
    """Performs OCR recognition on a Base64 string or remote image URL."""
    try:
        payload = request.image_url if request.image_url else request.image_base64
        is_url = bool(request.image_url)
        return orchestrator.process_image(
            payload=payload,
            is_url=is_url,
            lang=request.lang,
            det=request.det if request.det is not None else True,
            rec=request.rec if request.rec is not None else True,
            cls=request.cls,
            min_confidence=request.min_confidence or 0.4,
            return_annotated_image=request.return_annotated_image,
            sort_reading_order=request.sort_reading_order,
            ocr_version=request.ocr_version,
        )
    except ImageCodecError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        )


@ocr_router.post("/upload", response_model=OCRResponse)
async def upload_and_ocr(
    file: UploadFile = File(..., description="Image file to process (JPEG, PNG, WEBP, BMP)"),
    lang: Optional[str] = Query(None, description="OCR language code (e.g. 'en', 'ch')"),
    ocr_version: Optional[str] = Query(None, description="OCR architecture override: 'PP-OCRv4', 'PP-OCRv3', 'PP-OCRv6'"),
    det: bool = Query(True, description="Enable text detection"),
    rec: bool = Query(True, description="Enable text recognition"),
    cls: Optional[bool] = Query(None, description="Enable orientation classifier"),
    min_confidence: float = Query(0.4, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    return_annotated_image: bool = Query(False, description="Return base64 annotated image"),
    sort_reading_order: bool = Query(True, description="Sort reading order"),
    orchestrator: OCROrchestratorService = Depends(get_ocr_orchestrator),
) -> OCRResponse:
    """Performs OCR recognition on an uploaded multipart image file."""
    try:
        contents = await file.read()
        return orchestrator.process_image(
            payload=contents,
            is_url=False,
            lang=lang,
            det=det,
            rec=rec,
            cls=cls,
            min_confidence=min_confidence,
            return_annotated_image=return_annotated_image,
            sort_reading_order=sort_reading_order,
            ocr_version=ocr_version,
        )
    except ImageCodecError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        )
