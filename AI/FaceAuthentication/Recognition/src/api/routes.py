"""
FastAPI REST API Routes for Face Detection, Cropping, Embedding, Verification, and Enrollment.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from src.schemas.request_schemas import (
    Base64ImagePayload,
    EnrollRequest,
    IdentifyRequest,
    VerifyBase64Request,
)
from src.schemas.response_schemas import (
    CropResponse,
    DetectResponse,
    EmbeddingResponse,
    EnrollResponse,
    IdentifyResponse,
    VerifyResponse,
)
from src.services.orchestrator import FaceRecognitionService

router = APIRouter(prefix="/api/v1", tags=["Face Recognition"])


def get_recognition_service() -> FaceRecognitionService:
    """Dependency injection provider for FaceRecognitionService."""
    from src.api.app import app_state
    return app_state.recognition_service


@router.get("/health")
def health_check():
    """Service health check endpoint."""
    return {"status": "healthy", "service": "Face Recognition API"}


# ==========================================
# 1. Detection Endpoints
# ==========================================
@router.post("/detect", response_model=DetectResponse, summary="Detect faces (Base64 JSON)")
def detect_faces_json(
    payload: Base64ImagePayload,
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """Detects faces from a base64 encoded image string."""
    try:
        return service.detect_faces(payload.image_base64)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/detect/file", response_model=DetectResponse, summary="Detect faces (Multipart File)")
async def detect_faces_file(
    file: UploadFile = File(...),
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """Detects faces from a multipart uploaded image file."""
    try:
        image_bytes = await file.read()
        return service.detect_faces(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# 2. Crop & Align Endpoints
# ==========================================
@router.post("/crop", response_model=CropResponse, summary="Align & Crop face (Base64 JSON)")
def crop_face_json(
    payload: Base64ImagePayload,
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """Detects, aligns (112x112 canonical), and returns base64 cropped face."""
    try:
        return service.crop_face(payload.image_base64)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/crop/file", response_model=CropResponse, summary="Align & Crop face (Multipart File)")
async def crop_face_file(
    file: UploadFile = File(...),
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """Detects, aligns (112x112 canonical), and returns base64 cropped face from uploaded file."""
    try:
        image_bytes = await file.read()
        return service.crop_face(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# 3. Extract Embedding Endpoints
# ==========================================
@router.post("/embedding", response_model=EmbeddingResponse, summary="Extract 512-D Embedding (Base64 JSON)")
def extract_embedding_json(
    payload: Base64ImagePayload,
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """Extracts 512-D ArcFace L2-normalized feature embedding from base64 image."""
    try:
        return service.get_embedding(payload.image_base64)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/embedding/file", response_model=EmbeddingResponse, summary="Extract 512-D Embedding (Multipart File)")
async def extract_embedding_file(
    file: UploadFile = File(...),
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """Extracts 512-D ArcFace L2-normalized feature embedding from uploaded file."""
    try:
        image_bytes = await file.read()
        return service.get_embedding(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# 4. 1:1 Verification Endpoints
# ==========================================
@router.post("/verify", response_model=VerifyResponse, summary="1:1 Verification (Base64 JSON)")
def verify_json(
    request: VerifyBase64Request,
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """1:1 Face Verification comparing two base64 encoded images."""
    try:
        return service.verify(
            image1_input=request.image1_base64,
            image2_input=request.image2_base64,
            threshold=request.threshold,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/verify/file", response_model=VerifyResponse, summary="1:1 Verification (Multipart Files)")
async def verify_files(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    threshold: Optional[float] = Form(0.40),
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """1:1 Face Verification comparing two uploaded image files."""
    try:
        bytes1 = await file1.read()
        bytes2 = await file2.read()
        return service.verify(
            image1_input=bytes1,
            image2_input=bytes2,
            threshold=threshold,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# 5. 1:N Enrollment & Identification Endpoints
# ==========================================
@router.post("/enroll", response_model=EnrollResponse, summary="Enroll identity with photos")
def enroll_person(
    request: EnrollRequest,
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """Enrolls a person into the gallery using one or more facial photos."""
    try:
        return service.enroll(
            person_id=request.person_id,
            images_input=request.images_base64,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/identify", response_model=IdentifyResponse, summary="1:N Identification against gallery")
def identify_person(
    request: IdentifyRequest,
    service: FaceRecognitionService = Depends(get_recognition_service),
):
    """Searches a query face against all registered gallery identities."""
    try:
        return service.identify(
            query_image_input=request.image_base64,
            top_k=request.top_k or 1,
            threshold=request.threshold,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
