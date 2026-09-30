"""
Detection Services Package exporting BlazeFace service and Factory.
"""

from src.services.detection.blazeface_service import BlazeFaceDetectionService
from src.services.detection.factory import DetectionServiceFactory

__all__ = [
    "BlazeFaceDetectionService",
    "DetectionServiceFactory",
]
