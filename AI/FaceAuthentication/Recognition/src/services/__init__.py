"""
Hierarchical Services Root Package:
- Base Root Interfaces: src.services.base
- Detection Services: src.services.detection
- Preprocessing Services: src.services.preprocessing
- Embedding Services: src.services.embedding
- Image Codec Service: src.services.codec
- Domain Orchestrator: src.services.orchestrator
"""

# Base Interfaces
from src.services.base import (
    BaseFaceDetectionService,
    BaseFaceEmbeddingService,
    BaseFacePreprocessingService,
)

# Detection
from src.services.detection import (
    BlazeFaceDetectionService,
    DetectionServiceFactory,
)

# Preprocessing
from src.services.preprocessing import (
    BBoxCropPreprocessingService,
    CanonicalLandmarkPreprocessingService,
    PreprocessingServiceFactory,
)

# Embedding
from src.services.embedding import (
    ArcFaceEmbeddingService,
    EmbeddingServiceFactory,
)

# Codec & Orchestration
from src.services.codec import ImageCodecService, ImageService
from src.services.orchestrator import FaceRecognitionService

__all__ = [
    # Base
    "BaseFaceDetectionService",
    "BaseFacePreprocessingService",
    "BaseFaceEmbeddingService",
    # Detection
    "BlazeFaceDetectionService",
    "DetectionServiceFactory",
    # Preprocessing
    "CanonicalLandmarkPreprocessingService",
    "BBoxCropPreprocessingService",
    "PreprocessingServiceFactory",
    # Embedding
    "ArcFaceEmbeddingService",
    "EmbeddingServiceFactory",
    # Codec & Orchestrator
    "ImageCodecService",
    "ImageService",
    "FaceRecognitionService",
]
