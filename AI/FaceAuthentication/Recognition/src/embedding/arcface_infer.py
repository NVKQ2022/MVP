"""
ArcFace deep feature embedding extractor using ONNX Runtime.
Extracts 512-dimensional L2-normalized identity embeddings.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import onnxruntime as ort

from src.config import ARCFACE_MODEL_PATH, DEFAULT_SIMILARITY_THRESHOLD, EMBEDDING_DIM
from src.preprocessing.preprocessor import FacePreprocessor


class ArcFaceEmbedding:
    """
    ArcFace embedding inference engine.
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        preprocessor: Optional[FacePreprocessor] = None,
        use_cuda: bool = False,
    ):
        self.model_path = Path(model_path or ARCFACE_MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"ArcFace model not found at '{self.model_path}'. "
                "Please download the weights using the model downloader or check configuration."
            )

        self.preprocessor = preprocessor or FacePreprocessor()

        # Set up ONNX Runtime Session
        available_providers = ort.get_available_providers()
        providers = []
        if use_cuda and "CUDAExecutionProvider" in available_providers:
            providers.append("CUDAExecutionProvider")
        providers.append("CPUExecutionProvider")

        self.session = ort.InferenceSession(str(self.model_path), providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.embedding_dim = EMBEDDING_DIM

    def extract_feature(
        self,
        input_data: Union[np.ndarray, str, Path],
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Extracts 512-D ArcFace feature embedding for a single face.

        Args:
            input_data: Either:
                - Preprocessed 4D tensor (1, 3, 112, 112)
                - BGR face image ndarray (H, W, 3)
                - File path to face image
            normalize: If True, applies L2 normalization to the embedding vector.

        Returns:
            1D numpy array of shape (512,) representing the face embedding.
        """
        if isinstance(input_data, (str, Path)):
            tensor = self.preprocessor.preprocess_file(input_data)
        elif isinstance(input_data, np.ndarray):
            if input_data.ndim == 4:
                tensor = input_data
            elif input_data.ndim == 3:
                tensor = self.preprocessor.preprocess(input_data)
            else:
                raise ValueError(f"Unexpected image array shape: {input_data.shape}")
        else:
            raise TypeError("input_data must be a filepath or numpy ndarray")

        # Run ONNX inference
        outputs = self.session.run([self.output_name], {self.input_name: tensor})
        embedding = outputs[0][0].astype(np.float32)

        if normalize:
            norm = np.linalg.norm(embedding)
            if norm > 1e-6:
                embedding = embedding / norm

        return embedding

    def extract_features_batch(
        self,
        batch_input: Union[List[np.ndarray], np.ndarray],
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Extracts ArcFace embeddings for a batch of face images.

        Args:
            batch_input: List of BGR images or preprocessed 4D batch tensor (N, 3, 112, 112).

        Returns:
            2D numpy array of shape (N, 512).
        """
        if isinstance(batch_input, list):
            tensor = self.preprocessor.preprocess_batch(batch_input)
        elif isinstance(batch_input, np.ndarray):
            if batch_input.ndim == 4:
                tensor = batch_input
            else:
                raise ValueError(f"Batch array must be 4D (N, C, H, W), got shape: {batch_input.shape}")
        else:
            raise TypeError("batch_input must be a list of images or a 4D ndarray")

        outputs = self.session.run([self.output_name], {self.input_name: tensor})
        embeddings = outputs[0].astype(np.float32)

        if normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1e-6
            embeddings = embeddings / norms

        return embeddings

    @staticmethod
    def compute_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Computes cosine similarity between two normalized embeddings.
        Range: [-1.0, 1.0], where 1.0 is exact match.
        """
        return float(np.dot(emb1, emb2))

    @staticmethod
    def verify(
        emb1: np.ndarray,
        emb2: np.ndarray,
        threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> Tuple[bool, float]:
        """
        Verifies if two embeddings belong to the same person based on cosine similarity threshold.

        Returns:
            (is_match: bool, similarity_score: float)
        """
        score = float(np.dot(emb1, emb2))
        return score >= threshold, score
