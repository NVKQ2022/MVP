"""OCR Package: Production-ready Optical Character Recognition Subsystem."""

from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService
from OCR.services.ocr.factory import OCRFactory
from OCR.services.ocr.paddle_backend import PaddleOCRBackend
from OCR.services.ocr.mock_backend import MockOCRBackend
from OCR.services.base.base_ocr import BaseOCRBackend, RawOCRItem
from OCR.services.codec.image_codec import ImageCodecService, ImageCodecError
from OCR.services.visualizer.annotator import OCRVisualizerService
from OCR.schemas.request_schemas import OCRPredictRequest
from OCR.schemas.response_schemas import (
    OCRResponse,
    OCRLineItem,
    OCRMetadata,
    HealthResponse,
    BackendInfoResponse,
)
from OCR.config import settings

__all__ = [
    "OCROrchestratorService",
    "OCRFactory",
    "PaddleOCRBackend",
    "MockOCRBackend",
    "BaseOCRBackend",
    "RawOCRItem",
    "ImageCodecService",
    "ImageCodecError",
    "OCRVisualizerService",
    "OCRPredictRequest",
    "OCRResponse",
    "OCRLineItem",
    "OCRMetadata",
    "HealthResponse",
    "BackendInfoResponse",
    "settings",
]
