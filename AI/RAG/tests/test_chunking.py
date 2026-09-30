"""Unit tests for Chunking infrastructure and interface."""

import unittest

from src.infrastructure.chunking.fixed_size import FixedSizeChunker


class ChunkingTest(unittest.TestCase):
    def test_fixed_size_chunker_basic(self):
        chunker = FixedSizeChunker(chunk_size=10, overlap=2, drop_empty=True)
        text = "abcdefghijklmnopqrstuvwxyz"
        chunks = chunker.chunk(text)
        self.assertGreater(len(chunks), 1)
        # Check first chunk has size 10
        self.assertEqual(len(chunks[0]), 10)
        self.assertEqual(chunks[0], "abcdefghij")
        # Step is 10 - 2 = 8, so second chunk starts at index 8 ("ij...")
        self.assertEqual(chunks[1], "ijklmnopqr")

    def test_chunker_empty_string(self):
        chunker = FixedSizeChunker(chunk_size=100, overlap=10, drop_empty=True)
        self.assertEqual(chunker.chunk(""), [])
        self.assertEqual(chunker.chunk("   \n\t  "), [])

    def test_chunker_validation(self):
        with self.assertRaises(ValueError):
            FixedSizeChunker(chunk_size=0)
        with self.assertRaises(ValueError):
            FixedSizeChunker(chunk_size=50, overlap=-1)
        with self.assertRaises(ValueError):
            FixedSizeChunker(chunk_size=50, overlap=50)
        with self.assertRaises(ValueError):
            FixedSizeChunker(chunk_size=50, overlap=60)


if __name__ == "__main__":
    unittest.main()
