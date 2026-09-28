"""
Anti-Spoofing package exporting concrete service and factory.
"""

from src.services.antispoofing.factory import AntiSpoofingServiceFactory
from src.services.antispoofing.minifasnet_service import MiniFASNetAntiSpoofingService

__all__ = [
    "AntiSpoofingServiceFactory",
    "MiniFASNetAntiSpoofingService",
]
