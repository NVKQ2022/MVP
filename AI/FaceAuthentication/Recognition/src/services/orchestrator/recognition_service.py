"""
Face Recognition Domain Orchestrator: Coordinates Detection, Preprocessing,
Feature Embedding, Anti-Spoofing / Liveness Check, Verification, Enrollment, and Identification.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np

from src.config import (
    ANTISPOOFING_BACKBONE,
    DEFAULT_SIMILARITY_THRESHOLD,
    DETECTION_BACKBONE,
    EMBEDDING_BACKBONE,
    ENABLE_LIVENESS,
    LIVENESS_THRESHOLD,
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
    LivenessDTO,
    LivenessResponse,
    PureEmbeddingResponse,
    VerifyResponse,
)
from src.services.antispoofing.factory import AntiSpoofingServiceFactory
from src.services.base.base_antispoofing import BaseAntiSpoofingService
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
    Detection, Preprocessing, Feature Embedding, and Anti-Spoofing sub-services.
    """

    def __init__(
        self,
        detection_service: Optional[BaseFaceDetectionService] = None,
        preprocessing_service: Optional[BaseFacePreprocessingService] = None,
        embedding_service: Optional[BaseFaceEmbeddingService] = None,
        antispoofing_service: Optional[BaseAntiSpoofingService] = None,
        default_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        enable_liveness: bool = ENABLE_LIVENESS,
        liveness_threshold: float = LIVENESS_THRESHOLD,
    ):
        # Auto-instantiate backends via factories based on configuration
        self.detector = detection_service or DetectionServiceFactory.create(DETECTION_BACKBONE)
        self.preprocessor = preprocessing_service or PreprocessingServiceFactory.create(PREPROCESSING_TYPE)
        self.embedder = embedding_service or EmbeddingServiceFactory.create(EMBEDDING_BACKBONE)
        self.antispoof = antispoofing_service or AntiSpoofingServiceFactory.create(ANTISPOOFING_BACKBONE)
        self.default_threshold = default_threshold
        self.enable_liveness = enable_liveness
        self.liveness_threshold = liveness_threshold

        # In-memory identity gallery: {person_id: normalized_centroid_embedding}
        self._gallery: Dict[str, np.ndarray] = {}

    @property
    def backend_info(self) -> Dict[str, str]:
        """Returns details about the currently active model backends."""
        return {
            "detector": self.detector.model_name,
            "preprocessor": self.preprocessor.__class__.__name__,
            "embedder": self.embedder.model_name,
            "antispoof": self.antispoof.model_name,
            "embedding_dim": str(self.embedder.embedding_dim),
            "target_resolution": f"{self.preprocessor.target_size[0]}x{self.preprocessor.target_size[1]}",
            "liveness_enabled": str(self.enable_liveness),
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

    def check_liveness(self, image_input: Union[bytes, str, np.ndarray]) -> LivenessResponse:
        """
        Evaluates anti-spoofing and liveness on the prominent face in the image.
        Returns LivenessResponse containing attack classification and probabilities.
        """
        img_bgr = ImageCodecService.decode(image_input)
        best_face = self.detector.detect_best(img_bgr)

        if not best_face:
            return LivenessResponse(
                face_count=0,
                liveness=None,
                details="No face detected in the image.",
            )

        liveness_dto = self.antispoof.check_liveness(img_bgr, best_face.bbox)
        return LivenessResponse(
            face_count=1,
            liveness=liveness_dto,
            details=f"Face is {liveness_dto.label} (confidence: {liveness_dto.confidence:.4f})",
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

    def get_live_face_embedding(
        self,
        image_input: Union[bytes, str, np.ndarray],
    ) -> List[float]:
        """
        Receives a whole image, verifies face liveness to block spoof attacks,
        detects and aligns the face, and returns only the 512-D embedding vector.

        Pipeline:
        1. Decode whole image payload.
        2. Detect face in the whole image (BlazeFace).
        3. Check liveness / anti-spoofing with 2.7x context patch (MiniFASNet).
           Rejects with ValueError if spoof attack (print/replay) is detected.
        4. Geometry-align face into 112x112 canonical coordinates.
        5. Extract and L2-normalize 512-D deep feature vector.

        Returns:
            List[float]: The 512-D normalized face embedding vector.

        Raises:
            ValueError: If no face is detected or if liveness check fails.
        """
        img_bgr = ImageCodecService.decode(image_input)
        best_face = self.detector.detect_best(img_bgr)

        if not best_face:
            raise ValueError("No face detected in the provided image.")

        # Anti-spoofing liveness check on whole image + face bbox
        liveness = self.antispoof.check_liveness(img_bgr, best_face.bbox)
        if not liveness.is_real:
            attack_info = f" ({liveness.attack_type})" if liveness.attack_type else ""
            raise ValueError(
                f"Liveness check failed: Spoof attack detected{attack_info}. "
                f"Real face confidence: {liveness.confidence:.4f} < {self.liveness_threshold:.2f} threshold."
            )

        # Alignment and ArcFace embedding extraction
        aligned_bgr = self.preprocessor.align_and_crop(img_bgr, best_face)
        tensor = self.preprocessor.normalize_tensor(aligned_bgr)
        embedding = self.embedder.extract(tensor, normalize=True)

        return embedding.tolist()

    def verify(
        self,
        image1_input: Union[bytes, str, np.ndarray],
        image2_input: Union[bytes, str, np.ndarray],
        threshold: Optional[float] = None,
        check_liveness: Optional[bool] = None,
    ) -> VerifyResponse:
        """
        1:1 Face Verification comparing two face images with optional anti-spoofing liveness check.
        """
        thresh = threshold if threshold is not None else self.default_threshold
        perform_liveness = self.enable_liveness if check_liveness is None else check_liveness

        # Decode & Detect Image 1
        img1_bgr = ImageCodecService.decode(image1_input)
        best_face1 = self.detector.detect_best(img1_bgr)
        if not best_face1:
            raise ValueError("No face detected in Image 1.")

        # Decode & Detect Image 2
        img2_bgr = ImageCodecService.decode(image2_input)
        best_face2 = self.detector.detect_best(img2_bgr)
        if not best_face2:
            raise ValueError("No face detected in Image 2.")

        # Liveness Anti-Spoofing Verification
        liveness1_dto: Optional[LivenessDTO] = None
        liveness2_dto: Optional[LivenessDTO] = None

        if perform_liveness:
            liveness1_dto = self.antispoof.check_liveness(img1_bgr, best_face1.bbox)
            liveness2_dto = self.antispoof.check_liveness(img2_bgr, best_face2.bbox)

            if not liveness1_dto.is_real or not liveness2_dto.is_real:
                spoof_sources = []
                if not liveness1_dto.is_real:
                    spoof_sources.append(f"Image 1 ({liveness1_dto.attack_type or 'spoof'})")
                if not liveness2_dto.is_real:
                    spoof_sources.append(f"Image 2 ({liveness2_dto.attack_type or 'spoof'})")

                return VerifyResponse(
                    match=False,
                    similarity_score=0.0,
                    threshold=float(thresh),
                    status=f"REJECTED: Spoof attack detected in {', '.join(spoof_sources)}",
                    liveness1=liveness1_dto,
                    liveness2=liveness2_dto,
                )

        # Feature Extraction
        aligned1 = self.preprocessor.align_and_crop(img1_bgr, best_face1)
        tensor1 = self.preprocessor.normalize_tensor(aligned1)
        emb1 = self.embedder.extract(tensor1, normalize=True)

        aligned2 = self.preprocessor.align_and_crop(img2_bgr, best_face2)
        tensor2 = self.preprocessor.normalize_tensor(aligned2)
        emb2 = self.embedder.extract(tensor2, normalize=True)

        similarity = self.embedder.cosine_similarity(emb1, emb2)
        is_match = similarity >= thresh

        return VerifyResponse(
            match=is_match,
            similarity_score=float(similarity),
            threshold=float(thresh),
            status="MATCH (Same Person)" if is_match else "MISMATCH (Different Person)",
            liveness1=liveness1_dto,
            liveness2=liveness2_dto,
        )

    def enroll(
        self,
        person_id: str,
        images_input: List[Union[bytes, str, np.ndarray]],
        check_liveness: Optional[bool] = None,
    ) -> EnrollResponse:
        """
        Enrolls a person with one or more photos into gallery using centroid template averaging.
        Optionally validates liveness on each photo to prevent spoof enrollment.
        """
        if not images_input:
            raise ValueError("At least one facial photo is required for enrollment.")

        perform_liveness = self.enable_liveness if check_liveness is None else check_liveness
        embeddings: List[np.ndarray] = []

        for idx, img in enumerate(images_input):
            img_bgr = ImageCodecService.decode(img)
            face = self.detector.detect_best(img_bgr)
            if face is None:
                continue

            if perform_liveness:
                liveness = self.antispoof.check_liveness(img_bgr, face.bbox)
                if not liveness.is_real:
                    raise ValueError(
                        f"Enrollment rejected: Photo #{idx + 1} failed liveness check "
                        f"({liveness.attack_type or 'spoof'} detected)."
                    )

            aligned_bgr = self.preprocessor.align_and_crop(img_bgr, face)
            tensor = self.preprocessor.normalize_tensor(aligned_bgr)
            emb = self.embedder.extract(tensor, normalize=True)
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
        check_liveness: Optional[bool] = None,
    ) -> IdentifyResponse:
        """
        1:N Identification searching query face against enrolled gallery.
        Optionally validates query probe liveness to prevent spoof search.
        """
        if not self._gallery:
            raise ValueError("Gallery is currently empty. Please enroll identities first.")

        perform_liveness = self.enable_liveness if check_liveness is None else check_liveness
        img_bgr = ImageCodecService.decode(query_image_input)
        face = self.detector.detect_best(img_bgr)

        if face is None:
            raise ValueError("No face detected in the query image.")

        if perform_liveness:
            liveness = self.antispoof.check_liveness(img_bgr, face.bbox)
            if not liveness.is_real:
                raise ValueError(
                    f"Identification rejected: Query image failed liveness check "
                    f"({liveness.attack_type or 'spoof'} detected)."
                )

        aligned_bgr = self.preprocessor.align_and_crop(img_bgr, face)
        tensor = self.preprocessor.normalize_tensor(aligned_bgr)
        query_emb = self.embedder.extract(tensor, normalize=True)

        thresh = threshold if threshold is not None else self.default_threshold
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
        self.antispoof.close()
