"""Domain Orchestrator Facade coordinating multi-stage OCR pipelines."""

from typing import Union, Optional, List
import numpy as np

from OCR.config import settings
from OCR.schemas.response_schemas import (
    OCRResponse,
    OCRLineItem,
    OCRMetadata,
    BackendInfoResponse,
)
from OCR.services.base.base_ocr import BaseOCRBackend
from OCR.services.ocr.factory import OCRFactory
from OCR.services.codec.image_codec import ImageCodecService
from OCR.services.visualizer.annotator import OCRVisualizerService
from OCR.utils.ordering import ReadingOrderSorter
from OCR.utils.timing import timer_context
from OCR.utils.logger import get_logger

logger = get_logger(__name__)


class OCROrchestratorService:
    """Facade coordinating decoding, inference, postprocessing, reading-order sorting, and visualization."""

    def __init__(self, ocr_backend: Optional[BaseOCRBackend] = None):
        """Initializes the orchestrator with an injected or factory-created OCR backend."""
        self.ocr_backend: BaseOCRBackend = (
            ocr_backend
            or OCRFactory.create(
                backend_name=settings.ocr_backend,
                default_lang=settings.ocr_default_lang,
                use_gpu=settings.ocr_use_gpu,
                use_angle_cls=settings.ocr_use_angle_cls,
            )
        )
        logger.info(
            f"OCROrchestratorService initialized with backend: '{self.ocr_backend.backend_name}'"
        )

    def process_image(
        self,
        payload: Union[str, bytes, np.ndarray],
        is_url: bool = False,
        lang: Optional[str] = None,
        det: bool = True,
        rec: bool = True,
        cls: bool = True,
        min_confidence: float = 0.5,
        return_annotated_image: bool = False,
        sort_reading_order: bool = True,
    ) -> OCRResponse:
        """Executes the end-to-end OCR processing pipeline.

        Args:
            payload: Base64 string, URL, raw bytes, or image array.
            is_url: Whether payload is an image URL.
            lang: Language override.
            det: Enable text detection.
            rec: Enable text recognition.
            cls: Enable angle classifier.
            min_confidence: Threshold score (0.0 to 1.0).
            return_annotated_image: Return base64 preview image with bounding boxes.
            sort_reading_order: Sort lines top-to-bottom, left-to-right.

        Returns:
            OCRResponse DTO with recognized text and metadata.
        """
        with timer_context() as total_timer:
            # 1. Universal Payload Decoding & Normalization
            image = ImageCodecService.decode(payload, is_url=is_url)
            h, w = image.shape[:2]

            # 2. OCR Inference
            with timer_context() as infer_timer:
                raw_items = self.ocr_backend.predict(
                    image=image,
                    lang=lang,
                    det=det,
                    rec=rec,
                    cls=cls,
                )

            # 3. Filter by confidence threshold
            effective_threshold = max(0.0, min(1.0, min_confidence))
            filtered_raw = [
                item for item in raw_items if item.confidence >= effective_threshold
            ]

            # 4. Reading Order Sorting (top-to-bottom, left-to-right)
            if sort_reading_order and filtered_raw:
                ordered_raw = ReadingOrderSorter.sort(filtered_raw)
            else:
                ordered_raw = filtered_raw

            # 5. Convert to response DTO line items
            line_items: List[OCRLineItem] = [
                OCRLineItem(
                    text=item.text,
                    confidence=item.confidence,
                    polygon=item.polygon,
                    box_2d=item.box_2d,
                )
                for item in ordered_raw
            ]

            # 6. Aggregate full text
            full_text = "\n".join(
                item.text for item in line_items if item.text.strip()
            )

            # 7. Optional Visual Annotation
            annotated_b64: Optional[str] = None
            if return_annotated_image:
                annotated_img = OCRVisualizerService.draw_annotations(
                    image=image,
                    ocr_items=line_items,
                )
                annotated_b64 = ImageCodecService.encode_base64(
                    annotated_img, extension=".jpg", quality=85
                )

        target_lang = lang or getattr(self.ocr_backend, "default_lang", settings.ocr_default_lang)
        device = "GPU" if getattr(self.ocr_backend, "use_gpu", False) else "CPU"

        metadata = OCRMetadata(
            backend=self.ocr_backend.backend_name,
            language=target_lang,
            image_width=w,
            image_height=h,
            processing_time_ms=total_timer["elapsed_ms"],
            inference_time_ms=infer_timer["elapsed_ms"],
            device=device,
        )

        return OCRResponse(
            success=True,
            message=f"Successfully extracted {len(line_items)} text line(s).",
            total_lines=len(line_items),
            full_text=full_text,
            lines=line_items,
            annotated_image_base64=annotated_b64,
            metadata=metadata,
        )

    def get_service_info(self) -> BackendInfoResponse:
        """Returns metadata about the active backend and capabilities."""
        return BackendInfoResponse(
            active_backend=self.ocr_backend.backend_name,
            available_backends=OCRFactory.list_available(),
            supported_languages=self.ocr_backend.supported_languages,
            use_gpu=getattr(self.ocr_backend, "use_gpu", False),
        )
