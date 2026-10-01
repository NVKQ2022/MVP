"""Server configuration settings."""

import os
from typing import List
from pydantic import BaseModel, Field


class ServerSettings(BaseModel):
    """Server runtime configuration loaded from environment or defaults."""

    app_name: str = Field(
        default_factory=lambda: os.getenv("APP_NAME", "ChatbotOCR API Service")
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
    allowed_cors_origins: List[str] = Field(
        default_factory=lambda: [origin.strip() for origin in os.getenv("ALLOWED_CORS_ORIGINS", "*").split(",")]
    )
    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )


server_settings = ServerSettings()
