"""
Main Application Entrypoint: Supports running the API Web Server, API Client Demo,
or executing modular operations via the Service Layer.
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn

from src.config import (
    API_HOST,
    API_PORT,
    DATA_DIR,
    DEFAULT_SIMILARITY_THRESHOLD,
    FACE_DIR,
    USE_ALIGNMENT,
)
from src.services.orchestrator import FaceRecognitionService
from src.utils.image_io import list_images, load_image
from src.utils.metrics import compute_pairwise_matrix, evaluate_dataset_verification


def print_banner():
    banner = """
========================================================================
   Face Recognition Service (BlazeFace + ArcFace)
   - Architecture: Hierarchical Service & Factory Pattern
   - API Support: REST Endpoints (FastAPI) & Request Payloads
   - Operations: Detect, Crop, 512-D Embedding, 1:1 Verify, 1:N Identify
========================================================================
"""
    print(banner)


def run_cli_pipeline(service: FaceRecognitionService, data_dir: Path, face_dir: Path):
    """Executes dataset crop, embedding, and verification matrix via Service class."""
    face_dir.mkdir(parents=True, exist_ok=True)
    images = list_images(data_dir, recursive=True)
    print(f"\n[1] Processing {len(images)} raw images from '{data_dir}'...")

    embeddings = {}
    for img_path in images:
        person_name = img_path.parent.name
        img_bgr = load_image(img_path)

        # Detect
        detection = service.detector.detect_best(img_bgr)
        if not detection:
            print(f"  [!] No face detected in: {img_path.name}")
            continue

        # Align & Crop via PreprocessingService
        aligned_bgr = service.preprocessor.align_and_crop(img_bgr, detection)

        # Save to Face/
        person_face_dir = face_dir / person_name
        person_face_dir.mkdir(parents=True, exist_ok=True)
        save_path = person_face_dir / img_path.name
        import cv2
        cv2.imwrite(str(save_path), aligned_bgr)

        # Extract 512-D ArcFace Embedding
        tensor = service.preprocessor.normalize_tensor(aligned_bgr)
        emb = service.embedder.extract(tensor, normalize=True)
        rel_key = f"{person_name}/{img_path.name}"
        embeddings[rel_key] = emb

    print(f" Cropped faces saved to '{face_dir}'")
    print(f" Extracted {len(embeddings)} ArcFace 512-D embeddings.")

    # Evaluate dataset verification
    if embeddings:
        print("\n[2] Verification & Authenticity Metrics:")
        metrics = evaluate_dataset_verification(embeddings, threshold=service.default_threshold)
        print(f"  Intra-person (Genuine) Similarity Mean: {metrics['intra_mean']:.4f}")
        print(f"  Inter-person (Imposter) Similarity Mean: {metrics['inter_mean']:.4f}")
        print(f"  True Accept Rate @ {service.default_threshold}: {metrics['true_accept_rate']:.2f}%")
        print(f"  False Accept Rate @ {service.default_threshold}: {metrics['false_accept_rate']:.2f}%")

        labels, matrix = compute_pairwise_matrix(embeddings)
        print("\nPairwise Similarity Matrix:")
        short_labels = [lbl.split("/")[-1].replace(".jpg", "") for lbl in labels]
        header = f"{'Image':<16} | " + " | ".join(f"{lbl:>8}" for lbl in short_labels)
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        for i, row_lbl in enumerate(short_labels):
            row_str = f"{row_lbl:<16} | " + " | ".join(
                f"{matrix[i, j]:>8.4f}" if i != j else f"{'1.0000':>8}"
                for j in range(len(short_labels))
            )
            print(row_str)
        print("-" * len(header))


def main():
    parser = argparse.ArgumentParser(
        description="Face Recognition Service & API Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the FastAPI REST API web server.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the API client simulation demo (fakes API requests with local Data/).",
    )
    parser.add_argument(
        "--action",
        choices=["all", "verify"],
        default="all",
        help="CLI action: 'all' (process dataset) or 'verify' (compare two images).",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=API_HOST,
        help="API host address.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=API_PORT,
        help="API port.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_SIMILARITY_THRESHOLD,
        help="Cosine similarity verification threshold.",
    )
    parser.add_argument(
        "--img1",
        type=Path,
        help="First image for 1:1 verification.",
    )
    parser.add_argument(
        "--img2",
        type=Path,
        help="Second image for 1:1 verification.",
    )

    args = parser.parse_args()
    print_banner()

    if args.serve:
        print(f" Starting FastAPI Server at http://{args.host}:{args.port}")
        print(f" Interactive Swagger API Docs available at http://{args.host}:{args.port}/docs")
        uvicorn.run("src.api.app:app", host=args.host, port=args.port, reload=False)
        return

    if args.demo:
        from run_api_demo import run_demo
        run_demo()
        return

    # Service Layer Execution
    service = FaceRecognitionService(default_threshold=args.threshold)
    try:
        if args.action == "verify":
            if not args.img1 or not args.img2:
                print("Error: --img1 and --img2 are required for verify action.")
                sys.exit(1)
            result = service.verify(args.img1, args.img2, threshold=args.threshold)
            print(f"Image 1: {args.img1}")
            print(f"Image 2: {args.img2}")
            print(f"Similarity Score: {result.similarity_score:.4f} (Threshold: {result.threshold:.2f})")
            print(f"Decision: {result.status}")
        else:
            run_cli_pipeline(service, DATA_DIR, FACE_DIR)
    finally:
        service.close()


if __name__ == "__main__":
    main()
