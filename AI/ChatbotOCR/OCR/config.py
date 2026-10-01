import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env from project root if available
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


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

    # OCR Model & Performance Settings
    ocr_backend: str = Field(
        default_factory=lambda: os.getenv("OCR_BACKEND", "paddle")
    )
    ocr_version: str = Field(
        default_factory=lambda: os.getenv("OCR_VERSION", "PP-OCRv4")
    )
    ocr_default_lang: str = Field(
        default_factory=lambda: os.getenv("OCR_LANG", "en")
    )
    ocr_use_gpu: bool = Field(
        default_factory=lambda: os.getenv("OCR_USE_GPU", "false").lower() in ("true", "1", "yes")
    )
    ocr_use_angle_cls: bool = Field(
        default_factory=lambda: os.getenv("OCR_USE_ANGLE_CLS", "false").lower() in ("true", "1", "yes")
    )
    ocr_use_doc_orientation: bool = Field(
        default_factory=lambda: os.getenv("OCR_USE_DOC_ORIENTATION", "false").lower() in ("true", "1", "yes")
    )
    ocr_use_doc_unwarping: bool = Field(
        default_factory=lambda: os.getenv("OCR_USE_DOC_UNWARPING", "false").lower() in ("true", "1", "yes")
    )
    ocr_det_limit_side_len: int = Field(
        default_factory=lambda: int(os.getenv("OCR_DET_LIMIT_SIDE_LEN", "960"))
    )
    ocr_max_side_len: int = Field(
        default_factory=lambda: int(os.getenv("OCR_MAX_SIDE_LEN", "0"))
    )
    ocr_det: bool = Field(
        default_factory=lambda: os.getenv("OCR_DET", "true").lower() in ("true", "1", "yes")
    )
    ocr_rec: bool = Field(
        default_factory=lambda: os.getenv("OCR_REC", "true").lower() in ("true", "1", "yes")
    )
    ocr_cls: bool = Field(
        default_factory=lambda: os.getenv("OCR_CLS", "false").lower() in ("true", "1", "yes")
    )
    ocr_min_confidence: float = Field(
        default_factory=lambda: float(os.getenv("OCR_MIN_CONFIDENCE", "0.4"))
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
