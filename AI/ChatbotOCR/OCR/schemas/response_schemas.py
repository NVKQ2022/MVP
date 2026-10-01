"""Response DTO schemas for OCR API endpoints."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class OCRLineItem(BaseModel):
    """Represents a single recognized text line/box."""

    text: str = Field(..., description="Recognized text string")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    polygon: List[List[int]] = Field(
        ...,
        description="4-point polygon coordinates [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]",
        examples=[[[10, 10], [100, 10], [100, 40], [10, 40]]],
    )
    box_2d: List[int] = Field(
        ...,
        description="Standard 2D bounding box [xmin, ymin, xmax, ymax]",
        examples=[[10, 10, 100, 40]],
    )


class OCRMetadata(BaseModel):
    """Execution metadata and performance metrics."""

    backend: str = Field(..., description="OCR Backend engine used (e.g. PaddleOCR, MockOCR)")
    language: str = Field(..., description="Language model used for OCR")
    image_width: int = Field(..., description="Input image width in pixels")
    image_height: int = Field(..., description="Input image height in pixels")
    processing_time_ms: float = Field(..., description="Total pipeline execution time in milliseconds")
    inference_time_ms: float = Field(..., description="Raw model inference time in milliseconds")
    device: str = Field(..., description="Device used for inference (CPU / GPU)")


class OCRResponse(BaseModel):
    """Main response structure for OCR prediction and upload endpoints."""

    success: bool = Field(default=True, description="Indicates if the OCR operation was successful")
    message: str = Field(default="OCR completed successfully", description="Status or summary message")
    total_lines: int = Field(..., description="Total number of text lines detected")
    full_text: str = Field(..., description="All recognized text lines joined by newlines in reading order")
    lines: List[OCRLineItem] = Field(default_factory=list, description="Detailed list of detected text boxes")
    annotated_image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded JPEG image with bounding boxes drawn (if requested)",
    )
    metadata: OCRMetadata = Field(..., description="Execution metadata and timings")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field("healthy", description="Service health status ('healthy' or 'degraded')")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    backend: str = Field(..., description="Current active OCR backend")
    device: str = Field(..., description="Execution device")


class BackendInfoResponse(BaseModel):
    """OCR Backend information and capabilities."""

    active_backend: str = Field(..., description="Active OCR backend identifier")
    available_backends: List[str] = Field(..., description="List of registered OCR backends")
    supported_languages: List[str] = Field(..., description="List of supported language codes")
    use_gpu: bool = Field(..., description="Whether GPU acceleration is enabled")
