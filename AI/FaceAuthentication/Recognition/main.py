"""
Command-Line Interface for Face Detection, Cropping, Preprocessing, and ArcFace Inference.
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    DATA_DIR,
    DEFAULT_SIMILARITY_THRESHOLD,
    FACE_DIR,
    USE_ALIGNMENT,
)
from src.pipeline import FaceRecognitionPipeline
from src.utils.metrics import compute_pairwise_matrix


def print_banner():
    banner = """
========================================================================
   Face Detection & ArcFace Feature Embedding Pipeline
   - Detection: MediaPipe BlazeFace
   - Alignment: 4-Point Canonical Similarity Transform (112x112)
   - Preprocessing: BGR -> RGB, Standard ArcFace Normalization
   - Feature Extractor: ArcFace Deep Embedding (512-D L2 Normalized)
========================================================================
"""
    print(banner)


def print_similarity_table(labels, matrix):
    """
    Nicely prints pairwise similarity matrix table.
    """
    print("\nPairwise Cosine Similarity Matrix:")
    short_labels = [lbl.split("/")[-1].replace(".jpg", "") for lbl in labels]
    
    # Header
    header = f"{'Image':<18} | " + " | ".join(f"{lbl:>10}" for lbl in short_labels)
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    # Rows
    for i, row_label in enumerate(short_labels):
        row_str = f"{row_label:<18} | " + " | ".join(
            f"{matrix[i, j]:>10.4f}" if i != j else f"{'1.0000':>10}"
            for j in range(len(short_labels))
        )
        print(row_str)
    print("-" * len(header))


def main():
    parser = argparse.ArgumentParser(
        description="Face Detection (BlazeFace) & Embedding (ArcFace) Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--action",
        choices=["all", "detect", "embed", "verify"],
        default="all",
        help="Action to perform: 'all' (run full pipeline), 'detect' (crop Data/ -> Face/), "
             "'embed' (extract embeddings from Face/), 'verify' (compare two images)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Path to raw dataset directory containing person folders.",
    )
    parser.add_argument(
        "--face-dir",
        type=Path,
        default=FACE_DIR,
        help="Path to output directory for cropped face images.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_SIMILARITY_THRESHOLD,
        help="Cosine similarity threshold for verification.",
    )
    parser.add_argument(
        "--no-align",
        action="store_true",
        help="Disable landmark alignment (uses bounding box margin crop instead).",
    )
    parser.add_argument(
        "--img1",
        type=Path,
        help="First image path for verification (used with --action verify).",
    )
    parser.add_argument(
        "--img2",
        type=Path,
        help="Second image path for verification (used with --action verify).",
    )

    args = parser.parse_args()
    print_banner()

    pipeline = FaceRecognitionPipeline(
        data_dir=args.data_dir,
        face_dir=args.face_dir,
        use_alignment=not args.no_align,
        similarity_threshold=args.threshold,
    )

    try:
        if args.action == "verify":
            if not args.img1 or not args.img2:
                print("Error: --img1 and --img2 are required when --action is 'verify'")
                sys.exit(1)

            print(f"Comparing Image 1: {args.img1}")
            print(f"       with Image 2: {args.img2}\n")
            result = pipeline.verify_two_images(args.img1, args.img2)
            if "error" in result:
                print(f"[!] Error: {result['error']}")
            else:
                print(f"Similarity Score: {result['similarity']:.4f} (Threshold: {result['threshold']:.2f})")
                print(f"Verification Result: {' MATCH (Same Person)' if result['match'] else ' MISMATCH (Different Person)'}")

        elif args.action == "detect":
            pipeline.detect_and_crop_dataset()

        elif args.action == "embed":
            embeddings = pipeline.extract_embeddings_from_face_dir()
            if embeddings:
                labels, matrix = compute_pairwise_matrix(embeddings)
                print_similarity_table(labels, matrix)

        elif args.action == "all":
            embeddings = pipeline.run_full_pipeline()
            if embeddings:
                labels, matrix = compute_pairwise_matrix(embeddings)
                print_similarity_table(labels, matrix)

    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
