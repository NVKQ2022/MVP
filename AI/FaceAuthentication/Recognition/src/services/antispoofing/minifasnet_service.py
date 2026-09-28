"""
MiniFASNet Face Anti-Spoofing and Liveness Verification Service using ONNX Runtime.
Implements patch-based liveness classification based on Silent-Face-Anti-Spoofing.
"""

from pathlib import Path
from typing import Optional, Tuple, Union
import cv2
import numpy as np
import onnxruntime as ort

from src.config import LIVENESS_THRESHOLD, MINIFASNET_MODEL_PATH
from src.schemas.response_schemas import BoundingBoxDTO, LivenessDTO
from src.services.base.base_antispoofing import BaseAntiSpoofingService


class MiniFASNetAntiSpoofingService(BaseAntiSpoofingService):
    """
    Concrete Face Anti-Spoofing Service using MiniFASNetV2 ONNX model.
    Detects 2D printed photo attacks and digital screen replay attacks.
    """

    def __init__(
        self,
        model_path: Union[str, Path] = MINIFASNET_MODEL_PATH,
        threshold: float = LIVENESS_THRESHOLD,
        scale: float = 2.7,
        target_size: Tuple[int, int] = (80, 80),
    ):
        self.model_path = Path(model_path)
        self.threshold = threshold
        self.scale = scale
        self.target_size = target_size

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"MiniFASNet model not found at '{self.model_path}'. "
                "Please run `python models/download_models.py` first."
            )

        # Initialize ONNX inference session
        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 2
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        self.session = ort.InferenceSession(
            str(self.model_path),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        self.input_name = self.session.get_inputs()[0].name

    @property
    def model_name(self) -> str:
        return "MiniFASNetV2"

    def _crop_expanded_patch(
        self,
        image_bgr: np.ndarray,
        bbox: BoundingBoxDTO,
    ) -> np.ndarray:
        """
        Crops face region scaled by factor (default 2.7) to incorporate surrounding
        context (hair, frame boundaries, background) critical for spoof detection.
        """
        src_h, src_w = image_bgr.shape[:2]
        box_w = max(bbox.width, 1)
        box_h = max(bbox.height, 1)

        scale = min((src_h - 1) / box_h, min((src_w - 1) / box_w, self.scale))
        new_w = box_w * scale
        new_h = box_h * scale

        cx = bbox.origin_x + box_w / 2.0
        cy = bbox.origin_y + box_h / 2.0

        x1 = max(0, int(cx - new_w / 2.0))
        y1 = max(0, int(cy - new_h / 2.0))
        x2 = min(src_w - 1, int(cx + new_w / 2.0))
        y2 = min(src_h - 1, int(cy + new_h / 2.0))

        patch = image_bgr[y1:y2 + 1, x1:x2 + 1]
        if patch.size == 0 or patch.shape[0] < 2 or patch.shape[1] < 2:
            # Fallback to direct bbox crop
            fb_x1 = max(0, bbox.origin_x)
            fb_y1 = max(0, bbox.origin_y)
            fb_x2 = min(src_w - 1, bbox.origin_x + box_w)
            fb_y2 = min(src_h - 1, bbox.origin_y + box_h)
            patch = image_bgr[fb_y1:fb_y2 + 1, fb_x1:fb_x2 + 1]

        return cv2.resize(patch, self.target_size, interpolation=cv2.INTER_AREA)

    def check_liveness(
        self,
        image_bgr: np.ndarray,
        bbox: BoundingBoxDTO,
    ) -> LivenessDTO:
        """
        Evaluates face liveness and returns a LivenessDTO.

        Silent-Face-Anti-Spoofing MiniFASNet expects raw BGR float32 in range [0, 255]
        with tensor shape (1, 3, 80, 80).
        Class indices:
            0: 2D Print attack
            1: Real Face
            2: 2D Screen replay attack
        """
        patch = self._crop_expanded_patch(image_bgr, bbox)

        # Convert to BGR float32 in [0, 255] and reshape to (1, 3, 80, 80)
        blob = np.transpose(patch.astype(np.float32), (2, 0, 1))[np.newaxis, ...]

        # ONNX inference
        logits = self.session.run(None, {self.input_name: blob})[0][0]

        # Softmax probability distribution
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)

        real_confidence = float(probs[1])
        is_real = bool(real_confidence >= self.threshold)

        if is_real:
            label = "Real"
            attack_type = None
        else:
            label = "Spoof"
            attack_type = "print" if probs[0] > probs[2] else "replay"

        return LivenessDTO(
            is_real=is_real,
            confidence=round(real_confidence, 4),
            label=label,
            attack_type=attack_type,
            raw_scores=[round(float(p), 4) for p in probs],
        )

    def close(self) -> None:
        if hasattr(self, "session") and self.session is not None:
            del self.session
            self.session = None
