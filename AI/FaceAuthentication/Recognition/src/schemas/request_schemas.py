"""
Pydantic Request Schemas for Face Recognition API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Base64ImagePayload(BaseModel):
    """Payload containing a base64 encoded image."""
    image_base64: str = Field(..., description="Base64 encoded image string or data URI")


class VerifyBase64Request(BaseModel):
    """1:1 Verification request comparing two base64 images."""
    image1_base64: str = Field(..., description="Base64 string of first image")
    image2_base64: str = Field(..., description="Base64 string of second image")
    threshold: Optional[float] = Field(0.40, description="Cosine similarity threshold (default 0.40)")


class EnrollRequest(BaseModel):
    """Enrollment request to register a person's face into gallery."""
    person_id: str = Field(..., description="Unique person identifier (e.g., 'duke', 'user_101')")
    images_base64: List[str] = Field(..., min_length=1, description="List of base64 encoded facial photos")


class IdentifyRequest(BaseModel):
    """1:N Identification request to find best matching person in gallery."""
    image_base64: str = Field(..., description="Base64 encoded probe image")
    top_k: Optional[int] = Field(1, description="Number of top matches to return")
    threshold: Optional[float] = Field(0.40, description="Similarity threshold for identification")
