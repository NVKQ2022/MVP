"""PaddleOCR Backend Implementation."""

import os
import threading
from typing import List, Optional, Dict, Tuple, Any
import numpy as np

# Ensure Paddle environment flags are set to avoid PIR / oneDNN issues on CPU
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"

from paddleocr import PaddleOCR

from OCR.services.base.base_ocr import BaseOCRBackend, RawOCRItem
from OCR.utils.logger import get_logger

logger = get_logger(__name__)


class PaddleOCRBackend(BaseOCRBackend):
    """Concrete PaddleOCR Backend using PaddleOCR (PP-OCRv4 / PP-OCRv3 / PP-OCRv2)."""

    _instances_cache: Dict[Tuple[str, bool, bool], PaddleOCR] = {}
    _lock = threading.Lock()

    def __init__(
        self,
        default_lang: str = "en",
        use_gpu: bool = False,
        use_angle_cls: bool = True,
    ):
        self.default_lang = default_lang
        self.use_gpu = use_gpu
        self.use_angle_cls = use_angle_cls
        self._is_ready = False

        # Pre-initialize default language engine
        logger.info(
            f"Initializing PaddleOCRBackend (default_lang={self.default_lang}, use_gpu={self.use_gpu}, use_angle_cls={self.use_angle_cls})"
        )
        self._get_or_create_engine(self.default_lang, self.use_gpu, self.use_angle_cls)
        self._is_ready = True

    @classmethod
    def _get_or_create_engine(
        cls,
        lang: str,
        use_gpu: bool,
        use_angle_cls: bool,
    ) -> PaddleOCR:
        """Retrieves an existing cached PaddleOCR instance or creates a new one safely."""
        cache_key = (lang.lower(), use_gpu, use_angle_cls)
        with cls._lock:
            if cache_key not in cls._instances_cache:
                logger.info(f"Loading PaddleOCR model instance for cache key: {cache_key}")
                device_str = "gpu" if use_gpu else "cpu"
                
                # Attempt modern PaddleOCR (PaddleX 3.x) initialization
                try:
                    engine = PaddleOCR(
                        lang=lang.lower(),
                        device=device_str,
                        use_textline_orientation=use_angle_cls,
                    )
                except Exception as e:
                    logger.warning(f"PaddleOCR modern init failed ({e}), attempting legacy init...")
                    try:
                        engine = PaddleOCR(
                            lang=lang.lower(),
                            use_gpu=use_gpu,
                            use_angle_cls=use_angle_cls,
                        )
                    except Exception:
                        engine = PaddleOCR(lang=lang.lower())

                cls._instances_cache[cache_key] = engine
            return cls._instances_cache[cache_key]

    @property
    def backend_name(self) -> str:
        return "PaddleOCR"

    @property
    def supported_languages(self) -> List[str]:
        return [
            "en",
            "ch",
            "korean",
            "japan",
            "chinese_cht",
            "ta",
            "te",
            "ka",
            "latin",
            "arabic",
            "cyrillic",
            "devanagari",
            "french",
            "german",
        ]

    def is_ready(self) -> bool:
        return self._is_ready

    def predict(
        self,
        image: np.ndarray,
        lang: Optional[str] = None,
        det: bool = True,
        rec: bool = True,
        cls: bool = True,
    ) -> List[RawOCRItem]:
        """Runs PaddleOCR prediction on the provided image."""
        if image is None or image.size == 0:
            return []

        target_lang = lang or self.default_lang
        engine = self._get_or_create_engine(
            lang=target_lang,
            use_gpu=self.use_gpu,
            use_angle_cls=cls if cls is not None else self.use_angle_cls,
        )

        with self._lock:
            # Modern PaddleOCR uses predict() or ocr()
            try:
                raw_output = engine.predict(image)
            except Exception as e:
                logger.warning(f"engine.predict failed, falling back to engine.ocr: {e}")
                raw_output = engine.ocr(image)

        return self._parse_output(raw_output)

    def _parse_output(self, raw_output: Any) -> List[RawOCRItem]:
        """Parses output from PaddleOCR (supporting both modern Paddlex dicts and legacy list format)."""
        items: List[RawOCRItem] = []

        if not raw_output:
            return items

        for page in raw_output:
            if page is None:
                continue

            # Case 1: PaddleX OCRResult dict-like structure (PaddleOCR 3.x+)
            if isinstance(page, dict) or hasattr(page, "keys"):
                rec_texts = page.get("rec_texts", [])
                rec_scores = page.get("rec_scores", [])
                rec_polys = page.get("rec_polys", [])
                rec_boxes = page.get("rec_boxes", [])

                total_entries = max(len(rec_texts), len(rec_polys))
                for i in range(total_entries):
                    text = rec_texts[i] if i < len(rec_texts) else ""
                    confidence = float(rec_scores[i]) if i < len(rec_scores) else 1.0

                    # Extract polygon
                    polygon: List[List[int]] = []
                    if i < len(rec_polys) and rec_polys[i] is not None:
                        poly_arr = np.array(rec_polys[i], dtype=int)
                        polygon = poly_arr.reshape(-1, 2).tolist()

                    # Extract or compute 2D bounding box [xmin, ymin, xmax, ymax]
                    box_2d: List[int] = []
                    if i < len(rec_boxes) and rec_boxes[i] is not None:
                        b = np.array(rec_boxes[i], dtype=int).tolist()
                        if len(b) == 4:
                            box_2d = [int(b[0]), int(b[1]), int(b[2]), int(b[3])]
                    
                    if not box_2d and polygon:
                        xs = [p[0] for p in polygon]
                        ys = [p[1] for p in polygon]
                        box_2d = [min(xs), min(ys), max(xs), max(ys)]

                    if text.strip() or polygon:
                        items.append(
                            RawOCRItem(
                                text=text.strip(),
                                confidence=round(confidence, 4),
                                polygon=polygon,
                                box_2d=box_2d,
                            )
                        )

            # Case 2: Legacy PaddleOCR format list of [[points], (text, confidence)]
            elif isinstance(page, list):
                for line in page:
                    if not line or len(line) < 2:
                        continue
                    poly_raw, text_score = line[0], line[1]
                    text, confidence = (
                        text_score[0],
                        float(text_score[1]),
                    ) if isinstance(text_score, (tuple, list)) else (str(text_score), 1.0)

                    polygon = [[int(pt[0]), int(pt[1])] for pt in poly_raw]
                    xs = [p[0] for p in polygon]
                    ys = [p[1] for p in polygon]
                    box_2d = [min(xs), min(ys), max(xs), max(ys)]

                    items.append(
                        RawOCRItem(
                            text=str(text).strip(),
                            confidence=round(confidence, 4),
                            polygon=polygon,
                            box_2d=box_2d,
                        )
                    )

        return items
