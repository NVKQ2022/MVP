"""
Base interfaces package exporting root abstract service definitions.
"""

from src.services.base.base_detection import BaseFaceDetectionService
from src.services.base.base_embedding import BaseFaceEmbeddingService
from src.services.base.base_preprocessing import BaseFacePreprocessingService

__all__ = [
    "BaseFaceDetectionService",
    "BaseFacePreprocessingService",
    "BaseFaceEmbeddingService",
]
