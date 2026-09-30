"""
Face verification metrics, distance calculations, and evaluation reporting.
"""

from typing import Dict, List, Tuple
import numpy as np


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Computes cosine similarity between two feature vectors: (v1 . v2) / (||v1|| * ||v2||).
    """
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Computes Euclidean distance between two vectors: ||v1 - v2||_2.
    """
    return float(np.linalg.norm(v1 - v2))


def compute_pairwise_matrix(
    embeddings_dict: Dict[str, np.ndarray]
) -> Tuple[List[str], np.ndarray]:
    """
    Computes NxN cosine similarity matrix for a dictionary of {image_name: embedding}.

    Returns:
        labels: List of image names/labels.
        matrix: NxN numpy similarity matrix.
    """
    labels = list(embeddings_dict.keys())
    n = len(labels)
    matrix = np.zeros((n, n), dtype=np.float32)

    for i in range(n):
        for j in range(n):
            matrix[i, j] = cosine_similarity(
                embeddings_dict[labels[i]],
                embeddings_dict[labels[j]],
            )

    return labels, matrix


def evaluate_dataset_verification(
    embeddings_dict: Dict[str, np.ndarray],
    threshold: float = 0.40,
) -> Dict[str, float]:
    """
    Evaluates intra-person (genuine) vs inter-person (imposter) verification metrics.
    Assumes image keys contain person identifier formatted as 'person/img.jpg' or 'person_img.jpg'.
    """
    keys = list(embeddings_dict.keys())
    
    intra_scores = []
    inter_scores = []

    for i in range(len(keys)):
        p1 = keys[i].split("/")[0] if "/" in keys[i] else keys[i].split("_")[0]
        for j in range(i + 1, len(keys)):
            p2 = keys[j].split("/")[0] if "/" in keys[j] else keys[j].split("_")[0]
            sim = cosine_similarity(embeddings_dict[keys[i]], embeddings_dict[keys[j]])
            if p1 == p2:
                intra_scores.append(sim)
            else:
                inter_scores.append(sim)

    intra_arr = np.array(intra_scores) if intra_scores else np.array([0.0])
    inter_arr = np.array(inter_scores) if inter_scores else np.array([0.0])

    true_accepts = np.sum(intra_arr >= threshold)
    false_rejects = np.sum(intra_arr < threshold)
    false_accepts = np.sum(inter_arr >= threshold)
    true_rejects = np.sum(inter_arr < threshold)

    tar = (true_accepts / len(intra_arr)) * 100 if len(intra_arr) > 0 else 0.0
    far = (false_accepts / len(inter_arr)) * 100 if len(inter_arr) > 0 else 0.0

    return {
        "intra_mean": float(np.mean(intra_arr)),
        "intra_min": float(np.min(intra_arr)),
        "intra_max": float(np.max(intra_arr)),
        "inter_mean": float(np.mean(inter_arr)),
        "inter_min": float(np.min(inter_arr)),
        "inter_max": float(np.max(inter_arr)),
        "true_accept_rate": float(tar),
        "false_accept_rate": float(far),
        "total_genuine_pairs": len(intra_scores),
        "total_imposter_pairs": len(inter_scores),
    }
