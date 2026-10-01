"""Mock OCR Backend implementation for fast automated testing and fallback."""

from typing import List, Optional
import numpy as np

from OCR.services.base.base_ocr import BaseOCRBackend, RawOCRItem
from OCR.utils.logger import get_logger

logger = get_logger(__name__)


class MockOCRBackend(BaseOCRBackend):
    """Deterministic Mock OCR engine for unit and integration testing without heavy models."""

    def __init__(self, default_text: Optional[str] = None, confidence: float = 0.98):
        self._default_text = default_text or "PaddleOCR Test Invoice\nTotal: $125.50"
        self._confidence = confidence
        self._is_ready = True
        logger.info("Initialized MockOCRBackend.")

    @property
    def backend_name(self) -> str:
        return "MockOCR"

    @property
    def supported_languages(self) -> List[str]:
        return ["en", "ch", "korean", "japan", "latin", "french", "german", "mock"]

    def is_ready(self) -> bool:
        return self._is_ready

    def predict(
        self,
        image: np.ndarray,
        lang: Optional[str] = None,
        det: bool = True,
        rec: bool = True,
        cls: Optional[bool] = None,
        ocr_version: Optional[str] = None,
    ) -> List[RawOCRItem]:
        """Generates deterministic mock OCR results based on image dimensions."""
        if image is None or image.size == 0:
            return []

        h, w = image.shape[:2]
        lines = self._default_text.splitlines()
        results: List[RawOCRItem] = []

        line_h = max(24, int(h / (len(lines) + 2)))
        for idx, line in enumerate(lines):
            ymin = int(20 + idx * (line_h + 10))
            ymax = int(ymin + line_h)
            xmin = 20
            xmax = min(w - 20, max(100, int(len(line) * 14)))

            polygon = [
                [xmin, ymin],
                [xmax, ymin],
                [xmax, ymax],
                [xmin, ymax],
            ]
            box_2d = [xmin, ymin, xmax, ymax]

            results.append(
                RawOCRItem(
                    text=line,
                    confidence=self._confidence,
                    polygon=polygon,
                    box_2d=box_2d,
                )
            )

        return results
