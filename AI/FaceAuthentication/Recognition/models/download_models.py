"""
Model download utility to fetch BlazeFace detector and ArcFace embedding models.
"""

import os
import urllib.request
import zipfile
from pathlib import Path
from tqdm import tqdm

MODELS_DIR = Path(__file__).resolve().parent

BLAZEFACE_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_detector/"
    "blaze_face_short_range/float16/latest/blaze_face_short_range.tflite"
)
BLAZEFACE_FILE = MODELS_DIR / "blaze_face_short_range.tflite"

ARCFACE_URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip"
ARCFACE_FILE = MODELS_DIR / "w600k_mbf.onnx"


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url: str, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with DownloadProgressBar(unit="B", unit_scale=True, miniters=1, desc=output_path.name) as t:
        urllib.request.urlretrieve(url, filename=str(output_path), reporthook=t.update_to)


def ensure_models():
    """Checks and downloads missing models."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. BlazeFace
    if not BLAZEFACE_FILE.exists():
        print(f"Downloading BlazeFace detector model to {BLAZEFACE_FILE}...")
        download_url(BLAZEFACE_URL, BLAZEFACE_FILE)
        print(" BlazeFace model downloaded.")
    else:
        print(f" BlazeFace model exists: {BLAZEFACE_FILE}")

    # 2. ArcFace
    if not ARCFACE_FILE.exists():
        print(f"Downloading ArcFace ONNX model to {ARCFACE_FILE}...")
        zip_path = MODELS_DIR / "buffalo_s.zip"
        download_url(ARCFACE_URL, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extract("w600k_mbf.onnx", path=str(MODELS_DIR))
        if zip_path.exists():
            zip_path.unlink()
        print(" ArcFace model downloaded and extracted.")
    else:
        print(f" ArcFace model exists: {ARCFACE_FILE}")


if __name__ == "__main__":
    ensure_models()
