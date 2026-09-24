"""
Abstract Root Base Class for all Face Feature Embedding Models.
"""

from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseFaceEmbeddingService(ABC):
    """
    Root Abstract Service for Deep Face Feature Extractor / Embedding Models.
    Subclasses wrap specific models (e.g. ArcFace, AdaFace, FaceNet, CosFace).
    """

    @abstractmethod
    def extract(self, tensor: np.ndarray, normalize: bool = True) -> np.ndarray:
        """
        Extracts a 1D deep feature embedding from a preprocessed tensor.

        Args:
            tensor: 4D float32 numpy tensor with shape (1, C, H, W).
            normalize: If True, applies L2 normalization to unit hypersphere.

        Returns:
            1D float32 numpy array representing the face embedding vector.
        """
        pass

    @abstractmethod
    def extract_batch(self, batch_tensor: np.ndarray, normalize: bool = True) -> np.ndarray:
        """
        Extracts deep feature embeddings for a batch of preprocessed faces.

        Args:
            batch_tensor: 4D float32 numpy tensor with shape (N, C, H, W).
            normalize: If True, applies L2 normalization per row.

        Returns:
            2D float32 numpy array with shape (N, embedding_dim).
        """
        pass

    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Dimensionality of the output embedding vector (e.g., 512)."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the human-readable model architecture identifier."""
        pass

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Computes cosine similarity between two embeddings.
        Assumes L2-normalized vectors (dot product).
        """
        return float(np.dot(emb1, emb2))

    def close(self) -> None:
        """Release inference session or GPU contexts. Default is no-op."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
