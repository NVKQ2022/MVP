"""
Global configuration for Face Detection, Preprocessing, and ArcFace Recognition.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
FACE_DIR = PROJECT_ROOT / "Face"
MODELS_DIR = PROJECT_ROOT / "models"
LIBS_DIR = PROJECT_ROOT / "libs" / "usr" / "lib" / "x86_64-linux-gnu"

# Model Paths
BLAZEFACE_MODEL_PATH = MODELS_DIR / "blaze_face_short_range.tflite"
ARCFACE_MODEL_PATH = MODELS_DIR / "w600k_mbf.onnx"

# BlazeFace Detection Parameters
DETECTION_CONFIDENCE_THRESHOLD = 0.5
CROP_MARGIN_RATIO = 0.15  # Expand bbox by 15% to ensure full face capture when cropping

# Preprocessing Parameters
TARGET_FACE_SIZE = (112, 112)  # ArcFace standard input size (width, height)
NORM_MEAN = 127.5
NORM_STD = 127.5  # Standard InsightFace normalization: (x - 127.5) / 127.5 -> [-1.0, 1.0]
USE_ALIGNMENT = True  # Enable 4-point/5-point similarity transformation alignment

# ArcFace Recognition Parameters
EMBEDDING_DIM = 512
DEFAULT_SIMILARITY_THRESHOLD = 0.40  # Cosine similarity threshold for verification
