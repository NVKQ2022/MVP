"""Services package."""

from OCR.services.base.base_ocr import BaseOCRBackend, RawOCRItem
from OCR.services.ocr.factory import OCRFactory
from OCR.services.ocr.paddle_backend import PaddleOCRBackend
from OCR.services.ocr.mock_backend import MockOCRBackend
from OCR.services.codec.image_codec import ImageCodecService, ImageCodecError
from OCR.services.visualizer.annotator import OCRVisualizerService
from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService

__all__ = [
    "BaseOCRBackend",
    "RawOCRItem",
    "OCRFactory",
    "PaddleOCRBackend",
    "MockOCRBackend",
    "ImageCodecService",
    "ImageCodecError",
    "OCRVisualizerService",
    "OCROrchestratorService",
]
