"""
Face Recognition Domain Orchestrator: Coordinates Detection, Preprocessing,
Feature Embedding, Verification, Multi-Photo Enrollment, and Identification.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np

from src.config import (
    DEFAULT_SIMILARITY_THRESHOLD,
    DETECTION_BACKBONE,
    EMBEDDING_BACKBONE,
    PREPROCESSING_TYPE,
)
from src.schemas.response_schemas import (
    CropResponse,
    DetectResponse,
    EmbeddingResponse,
    EnrollResponse,
    FaceDetectionDTO,
    IdentifyMatchDTO,
    IdentifyResponse,
    VerifyResponse,
)
from src.services.base.base_detection import BaseFaceDetectionService
from src.services.base.base_embedding import BaseFaceEmbeddingService
from src.services.base.base_preprocessing import BaseFacePreprocessingService
from src.services.codec.image_codec import ImageCodecService
from src.services.detection.factory import DetectionServiceFactory
from src.services.embedding.factory import EmbeddingServiceFactory
from src.services.preprocessing.factory import PreprocessingServiceFactory


class FaceRecognitionService:
    """
    Main Domain Orchestrator service implementing the Facade pattern over
    Detection, Preprocessing, and Embedding sub-services.
    """

    def __init__(
        self,
        detection_service: Optional[BaseFaceDetectionService] = None,
        preprocessing_service: Optional[BaseFacePreprocessingService] = None,
        embedding_service: Optional[BaseFaceEmbeddingService] = None,
        default_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        # Auto-instantiate backends via factories based on configuration
        self.detector = detection_service or DetectionServiceFactory.create(DETECTION_BACKBONE)
        self.preprocessor = preprocessing_service or PreprocessingServiceFactory.create(PREPROCESSING_TYPE)
        self.embedder = embedding_service or EmbeddingServiceFactory.create(EMBEDDING_BACKBONE)
        self.default_threshold = default_threshold

        # In-memory identity gallery: {person_id: normalized_centroid_embedding}
        self._gallery: Dict[str, np.ndarray] = {}

    @property
    def backend_info(self) -> Dict[str, str]:
        """Returns details about the currently active model backends."""
        return {
            "detector": self.detector.model_name,
            "embedder": self.embedder.model_name,
            "embedding_dim": self.embedder.embedding_dim,
            "target_resolution": f"{self.preprocessor.target_size[0]}x{self.preprocessor.target_size[1]}",
        }

    def detect_faces(self, image_input: Union[bytes, str, np.ndarray]) -> DetectResponse:
        """Detect all faces in an image payload."""
        faces = self.detector.detect(image_input)
        return DetectResponse(face_count=len(faces), faces=faces)

    def crop_face(self, image_input: Union[bytes, str, np.ndarray]) -> CropResponse:
        """Detect, align, and return cropped face as Base64 string."""
        img_bgr = ImageCodecService.decode(image_input)
        best_face = self.detector.detect_best(img_bgr)

        if not best_face:
            return CropResponse(face_count=0, image_width=0, image_height=0, cropped_face_base64=None)

        aligned_bgr = self.preprocessor.align_and_crop(img_bgr, best_face)
        h, w = aligned_bgr.shape[:2]
        base64_crop = ImageCodecService.encode_to_base64(aligned_bgr)

        return CropResponse(
            face_count=1,
            image_width=w,
            image_height=h,
            cropped_face_base64=base64_crop,
        )

    def extract_embedding_from_raw(
        self,
        image_input: Union[bytes, str, np.ndarray],
    ) -> Tuple[Optional[np.ndarray], Optional[FaceDetectionDTO]]:
        """Internal Helper: Detects face, aligns, and extracts normalized deep feature embedding."""
        img_bgr = ImageCodecService.decode(image_input)
        best_face = self.detector.detect_best(img_bgr)

        if not best_face:
            return None, None

        aligned_bgr = self.preprocessor.align_and_crop(img_bgr, best_face)
        tensor = self.preprocessor.normalize_tensor(aligned_bgr)
        embedding = self.embedder.extract(tensor, normalize=True)
        return embedding, best_face

    def get_embedding(self, image_input: Union[bytes, str, np.ndarray]) -> EmbeddingResponse:
        """Extract 512-D embedding vector from image."""
        embedding, _ = self.extract_embedding_from_raw(image_input)
        if embedding is None:
            raise ValueError("No face detected in the provided image.")

        return EmbeddingResponse(
            embedding_dim=len(embedding),
            embedding=embedding.tolist(),
        )

    def verify(
        self,
        image1_input: Union[bytes, str, np.ndarray],
        image2_input: Union[bytes, str, np.ndarray],
        threshold: Optional[float] = None,
    ) -> VerifyResponse:
        """1:1 Face Verification comparing two face images."""
        thresh = threshold if threshold is not None else self.default_threshold

        emb1, _ = self.extract_embedding_from_raw(image1_input)
        if emb1 is None:
            raise ValueError("No face detected in Image 1.")

        emb2, _ = self.extract_embedding_from_raw(image2_input)
        if emb2 is None:
            raise ValueError("No face detected in Image 2.")

        similarity = self.embedder.cosine_similarity(emb1, emb2)
        is_match = similarity >= thresh

        return VerifyResponse(
            match=is_match,
            similarity_score=float(similarity),
            threshold=float(thresh),
            status="MATCH (Same Person)" if is_match else "MISMATCH (Different Person)",
        )

    def enroll(
        self,
        person_id: str,
        images_input: List[Union[bytes, str, np.ndarray]],
    ) -> EnrollResponse:
        """
        Enrolls a person with one or more photos into gallery using centroid template averaging.
        """
        if not images_input:
            raise ValueError("At least one facial photo is required for enrollment.")

        embeddings: List[np.ndarray] = []
        for img in images_input:
            emb, _ = self.extract_embedding_from_raw(img)
            if emb is not None:
                embeddings.append(emb)

        if not embeddings:
            raise ValueError(f"Could not detect any valid face for person '{person_id}'.")

        # Compute centroid average
        centroid = np.mean(embeddings, axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 1e-6:
            centroid = centroid / norm

        self._gallery[person_id] = centroid

        return EnrollResponse(
            person_id=person_id,
            status="ENROLLED",
            enrolled_images_count=len(embeddings),
            total_gallery_identities=len(self._gallery),
        )

    def identify(
        self,
        query_image_input: Union[bytes, str, np.ndarray],
        top_k: int = 1,
        threshold: Optional[float] = None,
    ) -> IdentifyResponse:
        """1:N Identification searching query face against enrolled gallery."""
        if not self._gallery:
            raise ValueError("Gallery is currently empty. Please enroll identities first.")

        thresh = threshold if threshold is not None else self.default_threshold
        query_emb, _ = self.extract_embedding_from_raw(query_image_input)

        if query_emb is None:
            raise ValueError("No face detected in the query image.")

        candidates: List[IdentifyMatchDTO] = []
        for pid, ref_emb in self._gallery.items():
            sim = self.embedder.cosine_similarity(query_emb, ref_emb)
            candidates.append(
                IdentifyMatchDTO(
                    person_id=pid,
                    similarity_score=float(sim),
                    is_match=sim >= thresh,
                )
            )

        candidates.sort(key=lambda c: c.similarity_score, reverse=True)
        top_matches = candidates[:top_k]
        best_candidate = candidates[0] if candidates else None
        identified = bool(best_candidate and best_candidate.is_match)

        return IdentifyResponse(
            identified=identified,
            top_match=best_candidate,
            all_candidates=top_matches,
        )

    def close(self) -> None:
        """Releases underlying resources."""
        self.detector.close()
        self.embedder.close()
