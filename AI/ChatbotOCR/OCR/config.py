"""Application configuration module."""

import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment or defaults."""

    app_name: str = Field(
        default_factory=lambda: os.getenv("APP_NAME", "PaddleOCR API Service")
    )
    app_version: str = Field(
        default_factory=lambda: os.getenv("APP_VERSION", "1.0.0")
    )
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    )
    host: str = Field(
        default_factory=lambda: os.getenv("HOST", "0.0.0.0")
    )
    port: int = Field(
        default_factory=lambda: int(os.getenv("PORT", "8000"))
    )

    # OCR Settings
    ocr_backend: str = Field(
        default_factory=lambda: os.getenv("OCR_BACKEND", "paddle")
    )
    ocr_default_lang: str = Field(
        default_factory=lambda: os.getenv("OCR_LANG", "en")
    )
    ocr_use_gpu: bool = Field(
        default_factory=lambda: os.getenv("OCR_USE_GPU", "false").lower() in ("true", "1", "yes")
    )
    ocr_use_angle_cls: bool = Field(
        default_factory=lambda: os.getenv("OCR_USE_ANGLE_CLS", "true").lower() in ("true", "1", "yes")
    )
    ocr_det: bool = Field(
        default_factory=lambda: os.getenv("OCR_DET", "true").lower() in ("true", "1", "yes")
    )
    ocr_rec: bool = Field(
        default_factory=lambda: os.getenv("OCR_REC", "true").lower() in ("true", "1", "yes")
    )
    ocr_cls: bool = Field(
        default_factory=lambda: os.getenv("OCR_CLS", "true").lower() in ("true", "1", "yes")
    )
    ocr_min_confidence: float = Field(
        default_factory=lambda: float(os.getenv("OCR_MIN_CONFIDENCE", "0.5"))
    )

    # Network / Security / Limits
    max_image_size_mb: int = Field(
        default_factory=lambda: int(os.getenv("MAX_IMAGE_SIZE_MB", "20"))
    )
    request_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30.0"))
    )
    allowed_cors_origins: List[str] = Field(
        default_factory=lambda: os.getenv("ALLOWED_CORS_ORIGINS", "*").split(",")
    )
    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )


# Global singleton instance
settings = Settings()
