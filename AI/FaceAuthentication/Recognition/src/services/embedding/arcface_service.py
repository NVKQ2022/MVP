"""
ArcFace Embedding Service: Concrete implementation of BaseFaceEmbeddingService
wrapping ArcFace deep feature extraction models using ONNX Runtime.
"""

from pathlib import Path
from typing import Optional, Union

import numpy as np
import onnxruntime as ort

from src.config import ARCFACE_MODEL_PATH, EMBEDDING_DIM
from src.services.base.base_embedding import BaseFaceEmbeddingService


class ArcFaceEmbeddingService(BaseFaceEmbeddingService):
    """
    ArcFace ONNX Embedding Extractor.
    Inherits from BaseFaceEmbeddingService.
    Supports MobileFaceNet, ResNet-50 (w600k_r50), ResNet-100 (glint360k_r100) ONNX weights.
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        use_cuda: bool = False,
        embedding_dim: int = EMBEDDING_DIM,
    ):
        self.model_path = Path(model_path or ARCFACE_MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"ArcFace model file missing at '{self.model_path}'. "
                "Please run models/download_models.py to download."
            )

        self._embedding_dim = embedding_dim

        # Configure ONNX Runtime execution providers
        available_providers = ort.get_available_providers()
        providers = []
        if use_cuda and "CUDAExecutionProvider" in available_providers:
            providers.append("CUDAExecutionProvider")
        providers.append("CPUExecutionProvider")

        self.session = ort.InferenceSession(str(self.model_path), providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    @property
    def model_name(self) -> str:
        return f"ArcFace ONNX ({self.model_path.name})"

    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim

    def extract(self, tensor: np.ndarray, normalize: bool = True) -> np.ndarray:
        """
        Extracts a 512-D float32 embedding vector from a preprocessed (1, 3, 112, 112) tensor.
        """
        if tensor.ndim != 4 or tensor.shape[1:] != (3, 112, 112):
            raise ValueError(f"Expected tensor shape (1, 3, 112, 112), got {tensor.shape}")

        outputs = self.session.run([self.output_name], {self.input_name: tensor})
        embedding = outputs[0][0].astype(np.float32)

        if normalize:
            norm = np.linalg.norm(embedding)
            if norm > 1e-6:
                embedding = embedding / norm

        return embedding

    def extract_batch(self, batch_tensor: np.ndarray, normalize: bool = True) -> np.ndarray:
        """
        Extracts deep feature embeddings for a batch of preprocessed faces (N, 3, 112, 112).
        """
        if batch_tensor.ndim != 4 or batch_tensor.shape[1:] != (3, 112, 112):
            raise ValueError(f"Expected batch tensor shape (N, 3, 112, 112), got {batch_tensor.shape}")

        outputs = self.session.run([self.output_name], {self.input_name: batch_tensor})
        embeddings = outputs[0].astype(np.float32)

        if normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1e-6
            embeddings = embeddings / norms

        return embeddings

    def close(self) -> None:
        """Closes ONNX Runtime session."""
        self.session = None
