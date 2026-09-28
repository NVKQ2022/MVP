"""
Pydantic Response Schemas / Data Transfer Objects (DTOs) for Face Recognition API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBoxDTO(BaseModel):
    """Bounding box coordinates in integer pixels."""
    origin_x: int
    origin_y: int
    width: int
    height: int


class KeypointDTO(BaseModel):
    """2D facial landmark keypoint."""
    name: str
    x: float
    y: float


class FaceDetectionDTO(BaseModel):
    """Detected face metadata."""
    bbox: BoundingBoxDTO
    confidence: float
    keypoints: List[KeypointDTO]


class DetectResponse(BaseModel):
    """Response returned by detection endpoint."""
    success: bool = True
    face_count: int
    faces: List[FaceDetectionDTO]


class CropResponse(BaseModel):
    """Response returned by crop endpoint containing aligned face image."""
    success: bool = True
    face_count: int
    image_width: int
    image_height: int
    cropped_face_base64: Optional[str] = None


class EmbeddingResponse(BaseModel):
    """Response returned by feature embedding endpoint."""
    success: bool = True
    embedding_dim: int = 512
    embedding: List[float]


class LivenessDTO(BaseModel):
    """Face Anti-Spoofing and Liveness estimation result."""
    is_real: bool = Field(..., description="True if real live human face, False if spoof attack")
    confidence: float = Field(..., description="Probability of live face [0.0, 1.0]")
    label: str = Field(..., description="'Real' or 'Spoof'")
    attack_type: Optional[str] = Field(None, description="Attack classification ('print', 'replay', or None)")
    raw_scores: Optional[List[float]] = Field(None, description="Class probabilities [Print, Real, Replay]")


class LivenessResponse(BaseModel):
    """Response returned by Face Anti-Spoofing endpoint."""
    success: bool = True
    face_count: int
    liveness: Optional[LivenessDTO] = None
    details: Optional[str] = None


class VerifyResponse(BaseModel):
    """1:1 Verification decision response."""
    success: bool = True
    match: bool
    similarity_score: float
    threshold: float
    status: str
    liveness1: Optional[LivenessDTO] = None
    liveness2: Optional[LivenessDTO] = None


class EnrollResponse(BaseModel):
    """Enrollment confirmation response."""
    success: bool = True
    person_id: str
    status: str
    enrolled_images_count: int
    total_gallery_identities: int


class IdentifyMatchDTO(BaseModel):
    """Single candidate match in 1:N search."""
    person_id: str
    similarity_score: float
    is_match: bool


class IdentifyResponse(BaseModel):
    """1:N Identification search results."""
    success: bool = True
    identified: bool
    top_match: Optional[IdentifyMatchDTO] = None
    all_candidates: List[IdentifyMatchDTO] = []
