"""
Codec package exporting ImageCodecService.
"""

from src.services.codec.image_codec import ImageCodecService

# Backward-compatibility alias
ImageService = ImageCodecService

__all__ = ["ImageCodecService", "ImageService"]
