"""
End-to-End Face Processing Pipeline:
1. BlazeFace Detection on raw images in Data/
2. Face Alignment & Cropping into person subfolders in Face/
3. Preprocessing (Resize, RGB, Normalization, NCHW formatting)
4. ArcFace ONNX Inference & Feature Embedding
5. Similarity Matrix & Authentication Verification
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from tqdm import tqdm

from src.config import (
    DATA_DIR,
    DEFAULT_SIMILARITY_THRESHOLD,
    FACE_DIR,
    TARGET_FACE_SIZE,
    USE_ALIGNMENT,
)
from src.detection.blazeface_detector import BlazeFaceDetector
from src.embedding.arcface_infer import ArcFaceEmbedding
from src.preprocessing.face_cropper import FaceCropper
from src.preprocessing.preprocessor import FacePreprocessor
from src.utils.image_io import list_images, load_image
from src.utils.metrics import (
    compute_pairwise_matrix,
    cosine_similarity,
    evaluate_dataset_verification,
)


class FaceRecognitionPipeline:
    """
    Modular Face Recognition Pipeline coordinating detection, preprocessing,
    and ArcFace feature embedding.
    """

    def __init__(
        self,
        data_dir: Path = DATA_DIR,
        face_dir: Path = FACE_DIR,
        use_alignment: bool = USE_ALIGNMENT,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        self.data_dir = Path(data_dir)
        self.face_dir = Path(face_dir)
        self.use_alignment = use_alignment
        self.similarity_threshold = similarity_threshold

        # Initialize sub-modules
        self.detector = BlazeFaceDetector()
        self.cropper = FaceCropper(
            target_size=TARGET_FACE_SIZE,
            use_alignment=self.use_alignment,
            output_base_dir=self.face_dir,
        )
        self.preprocessor = FacePreprocessor(target_size=TARGET_FACE_SIZE)
        self.embedder = ArcFaceEmbedding(preprocessor=self.preprocessor)

    def detect_and_crop_dataset(
        self,
        input_data_dir: Optional[Path] = None,
        output_face_dir: Optional[Path] = None,
    ) -> Dict[str, List[Path]]:
        """
        Step 1: Detects faces from raw images in Data/ and saves cropped/aligned faces
        into Face/<person_name>/<filename>.

        Returns:
            Dictionary mapping person_name to list of saved face filepaths.
        """
        src_dir = Path(input_data_dir or self.data_dir)
        dst_dir = Path(output_face_dir or self.face_dir)
        dst_dir.mkdir(parents=True, exist_ok=True)

        image_paths = list_images(src_dir, recursive=True)
        print(f"\n[Step 1] Detecting faces from {len(image_paths)} raw images in '{src_dir}'...")

        saved_faces: Dict[str, List[Path]] = {}
        successful_crops = 0
        failed_detections = 0

        for img_path in tqdm(image_paths, desc="Detecting & Cropping Faces"):
            # Person folder name is the immediate parent directory or relative path
            person_name = img_path.parent.name
            if person_name not in saved_faces:
                saved_faces[person_name] = []

            img_bgr = load_image(img_path)
            detection = self.detector.detect_best(img_bgr)

            if detection is None:
                print(f"  [!] Warning: No face detected in '{img_path.relative_to(src_dir)}'")
                failed_detections += 1
                continue

            # Extract face using canonical alignment or bounded crop
            face_img = self.cropper.extract_face(img_bgr, detection, use_alignment=self.use_alignment)

            # Save to Face/<person_name>/<filename>
            saved_path = self.cropper.save_face(
                face_img=face_img,
                person_name=person_name,
                filename=img_path.name,
            )
            saved_faces[person_name].append(saved_path)
            successful_crops += 1

        print(
            f" Cropping Complete: {successful_crops} faces extracted and saved to '{dst_dir}'. "
            f"({failed_detections} failed)"
        )
        return saved_faces

    def extract_embeddings_from_face_dir(
        self,
        face_dir: Optional[Path] = None,
    ) -> Dict[str, np.ndarray]:
        """
        Step 2: Reads cropped face images from Face/ directory, preprocesses them,
        and extracts 512-D ArcFace feature embeddings.

        Returns:
            Dictionary mapping '<person_name>/<filename>' to 512-D normalized embedding.
        """
        faces_dir = Path(face_dir or self.face_dir)
        face_paths = list_images(faces_dir, recursive=True)

        print(f"\n[Step 2] Extracting ArcFace embeddings from {len(face_paths)} faces in '{faces_dir}'...")

        embeddings: Dict[str, np.ndarray] = {}
        for path in tqdm(face_paths, desc="ArcFace Inference"):
            rel_key = str(path.relative_to(faces_dir))
            face_bgr = load_image(path)
            emb = self.embedder.extract_feature(face_bgr, normalize=True)
            embeddings[rel_key] = emb

        print(f" Embedding Extraction Complete: {len(embeddings)} face vectors generated (dim=512).")
        return embeddings

    def process_single_image(
        self,
        image_input: Union[str, Path, np.ndarray],
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Processes a single raw image end-to-end:
        1. Detects face using BlazeFace
        2. Crops / Aligns face to 112x112
        3. Preprocesses & computes ArcFace embedding

        Returns:
            (cropped_face_bgr, 512d_embedding) or (None, None) if no face detected.
        """
        if isinstance(image_input, (str, Path)):
            img_bgr = load_image(image_input)
        else:
            img_bgr = image_input

        detection = self.detector.detect_best(img_bgr)
        if detection is None:
            return None, None

        face_bgr = self.cropper.extract_face(img_bgr, detection, use_alignment=self.use_alignment)
        emb = self.embedder.extract_feature(face_bgr, normalize=True)
        return face_bgr, emb

    def verify_two_images(
        self,
        image_path1: Union[str, Path],
        image_path2: Union[str, Path],
    ) -> Dict[str, Union[bool, float, str]]:
        """
        Verifies if two raw or cropped images belong to the same person.
        """
        face1, emb1 = self.process_single_image(image_path1)
        face2, emb2 = self.process_single_image(image_path2)

        if emb1 is None or emb2 is None:
            missing = []
            if emb1 is None:
                missing.append(str(image_path1))
            if emb2 is None:
                missing.append(str(image_path2))
            return {
                "match": False,
                "similarity": 0.0,
                "error": f"No face detected in: {', '.join(missing)}",
            }

        sim = cosine_similarity(emb1, emb2)
        is_match = sim >= self.similarity_threshold

        return {
            "match": is_match,
            "similarity": float(sim),
            "threshold": float(self.similarity_threshold),
            "status": "SAME PERSON" if is_match else "DIFFERENT PERSON",
        }

    def run_full_pipeline(self) -> Dict[str, np.ndarray]:
        """
        Executes complete pipeline:
        1. BlazeFace Detection & Cropping (Data/ -> Face/)
        2. ArcFace Preprocessing & Feature Extraction
        3. Dataset Similarity Evaluation & Metric Display
        """
        # Step 1: Detect & Crop
        self.detect_and_crop_dataset()

        # Step 2: ArcFace Feature Extraction
        embeddings = self.extract_embeddings_from_face_dir()

        # Step 3: Pairwise Analysis & Verification Report
        if embeddings:
            print("\n[Step 3] Verification & Authenticity Metrics Evaluation:")
            metrics = evaluate_dataset_verification(embeddings, threshold=self.similarity_threshold)
            print(f"  Intra-person (Genuine) Similarity Mean: {metrics['intra_mean']:.4f} "
                  f"(Range: [{metrics['intra_min']:.4f}, {metrics['intra_max']:.4f}])")
            print(f"  Inter-person (Imposter) Similarity Mean: {metrics['inter_mean']:.4f} "
                  f"(Range: [{metrics['inter_min']:.4f}, {metrics['inter_max']:.4f}])")
            print(f"  True Accept Rate @ threshold {self.similarity_threshold}: {metrics['true_accept_rate']:.2f}%")
            print(f"  False Accept Rate @ threshold {self.similarity_threshold}: {metrics['false_accept_rate']:.2f}%")

        return embeddings

    def close(self):
        """Release underlying detector and inference session resources."""
        self.detector.close()
