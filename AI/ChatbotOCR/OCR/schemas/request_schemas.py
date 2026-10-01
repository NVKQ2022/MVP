"""Request DTO schemas for OCR API endpoints."""

from typing import Optional
from pydantic import BaseModel, Field, model_validator


class OCRPredictRequest(BaseModel):
    """Payload for OCR prediction endpoint."""

    image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded image string (supports data URI schemes like data:image/png;base64,...)",
        examples=["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="],
    )
    image_url: Optional[str] = Field(
        default=None,
        description="Direct public HTTP/HTTPS URL of the image",
        examples=["https://example.com/sample_receipt.jpg"],
    )
    lang: Optional[str] = Field(
        default=None,
        description="OCR language code (e.g. 'en', 'ch', 'korean', 'japan', 'latin', 'french', 'german'). Defaults to server configuration if omitted.",
        examples=["en"],
    )
    det: Optional[bool] = Field(
        default=True,
        description="Whether to perform text detection (localize bounding boxes). Set to False for text recognition only.",
    )
    rec: Optional[bool] = Field(
        default=True,
        description="Whether to perform text recognition (read text content).",
    )
    cls: Optional[bool] = Field(
        default=True,
        description="Whether to use text orientation / angle classifier.",
    )
    min_confidence: Optional[float] = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score threshold (0.0 - 1.0) to filter low-confidence detections.",
    )
    return_annotated_image: bool = Field(
        default=False,
        description="If True, includes base64-encoded visual annotated image with bounding boxes drawn in response.",
    )
    sort_reading_order: bool = Field(
        default=True,
        description="If True, orders detected text lines top-to-bottom and left-to-right.",
    )
    ocr_version: Optional[str] = Field(
        default=None,
        description="OCR model architecture override: 'PP-OCRv4' (fast & balanced), 'PP-OCRv3' (ultra fast), or 'PP-OCRv6' (accurate server model).",
    )

    @model_validator(mode="after")
    def check_at_least_one_source(self) -> "OCRPredictRequest":
        if not self.image_base64 and not self.image_url:
            raise ValueError("Either 'image_base64' or 'image_url' must be provided in the request payload.")
        return self
