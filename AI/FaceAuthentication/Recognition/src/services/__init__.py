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
    BaseAntiSpoofingService,
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

# Anti-Spoofing & Liveness
from src.services.antispoofing import (
    AntiSpoofingServiceFactory,
    MiniFASNetAntiSpoofingService,
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
    "BaseAntiSpoofingService",
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
    # Anti-Spoofing
    "MiniFASNetAntiSpoofingService",
    "AntiSpoofingServiceFactory",
    # Embedding
    "ArcFaceEmbeddingService",
    "EmbeddingServiceFactory",
    # Codec & Orchestrator
    "ImageCodecService",
    "ImageService",
    "FaceRecognitionService",
]
