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


class VerifyResponse(BaseModel):
    """1:1 Verification decision response."""
    success: bool = True
    match: bool
    similarity_score: float
    threshold: float
    status: str


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
