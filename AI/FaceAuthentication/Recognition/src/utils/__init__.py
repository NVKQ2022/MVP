"""Utilities package exporting I/O and metric functions."""

from src.utils.image_io import draw_detection, list_images, load_image, save_image
from src.utils.metrics import (
    compute_pairwise_matrix,
    cosine_similarity,
    euclidean_distance,
    evaluate_dataset_verification,
)

__all__ = [
    "draw_detection",
    "list_images",
    "load_image",
    "save_image",
    "compute_pairwise_matrix",
    "cosine_similarity",
    "euclidean_distance",
    "evaluate_dataset_verification",
]
