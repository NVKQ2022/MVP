"""
Global configuration and environment settings with dynamic model backend selection.
"""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
FACE_DIR = PROJECT_ROOT / "Face"
MODELS_DIR = PROJECT_ROOT / "models"
LIBS_DIR = PROJECT_ROOT / "libs" / "usr" / "lib" / "x86_64-linux-gnu"

# ==============================================================================
# Model Backend Selectors (Config-driven switching)
# ==============================================================================
# Available Detection Backends: "blazeface"
DETECTION_BACKBONE = os.getenv("DETECTION_BACKBONE", "blazeface").lower()

# Available Embedding Backends: "arcface"
EMBEDDING_BACKBONE = os.getenv("EMBEDDING_BACKBONE", "arcface").lower()

# Available Preprocessing Backends: "landmark_affine", "bbox_crop"
PREPROCESSING_TYPE = os.getenv("PREPROCESSING_TYPE", "landmark_affine").lower()

# Model Weights Paths
BLAZEFACE_MODEL_PATH = Path(
    os.getenv("BLAZEFACE_MODEL_PATH", str(MODELS_DIR / "blaze_face_short_range.tflite"))
)
ARCFACE_MODEL_PATH = Path(
    os.getenv("ARCFACE_MODEL_PATH", str(MODELS_DIR / "w600k_mbf.onnx"))
)

# Hyperparameters
DETECTION_CONFIDENCE_THRESHOLD = float(os.getenv("DETECTION_CONFIDENCE_THRESHOLD", "0.50"))
CROP_MARGIN_RATIO = float(os.getenv("CROP_MARGIN_RATIO", "0.15"))
TARGET_FACE_SIZE = (112, 112)
NORM_MEAN = 127.5
NORM_STD = 127.5
USE_ALIGNMENT = os.getenv("USE_ALIGNMENT", "true").lower() in ("true", "1", "yes")

# Recognition & Verification Thresholds
EMBEDDING_DIM = 512
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.40"))

# API Server Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_TITLE = "Face Authentication & Recognition Service"
API_VERSION = "2.0.0"
