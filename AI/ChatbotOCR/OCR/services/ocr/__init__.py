"""OCR Services package."""

from OCR.services.ocr.paddle_backend import PaddleOCRBackend
from OCR.services.ocr.mock_backend import MockOCRBackend
from OCR.services.ocr.factory import OCRFactory

__all__ = ["PaddleOCRBackend", "MockOCRBackend", "OCRFactory"]
