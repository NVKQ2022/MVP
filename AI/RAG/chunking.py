"""Document chunking interface and implementations.

Delegates to Clean Architecture domain and infrastructure layers.
"""

from src.domain.interfaces.chunker import ChunkerInterface
from src.infrastructure.chunking.fixed_size import FixedSizeChunker

# Backward-compatible class aliases
ChunkingService = ChunkerInterface
FixedSizeChunkingService = FixedSizeChunker

__all__ = [
    "ChunkingService",
    "FixedSizeChunkingService",
]
