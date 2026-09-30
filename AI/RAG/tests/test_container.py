"""Unit tests for Container and Composition Root."""

import tempfile
import unittest

from src.container import Container
from src.infrastructure.config.settings import Settings


class ContainerTest(unittest.TestCase):
    def test_container_build_components(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = Settings(
                endpoint="https://mock.api.endpoint",
                provider="openai",
                api_key="mock-key",
                model_name="mock-gpt",
                embedding_model="text-embedding-3-small",
                chroma_persist_dir=temp_dir,
                chroma_collection="test_rfc",
            )
            container = Container(custom_settings)

            chunker = container.build_chunker(chunk_size=400, overlap=20)
            self.assertEqual(chunker.chunk_size, 400)
            self.assertEqual(chunker.overlap, 20)

            vector_store = container.build_vector_store()
            self.assertEqual(vector_store.collection_name, "test_rfc")

            llm = container.build_llm_client()
            self.assertEqual(llm.model_name, "mock-gpt")

            naive_rag = container.build_naive_rag(vector_store=vector_store, llm_client=llm)
            self.assertIsNotNone(naive_rag)

            agentic_rag = container.build_agentic_rag(naive_rag=naive_rag, llm_client=llm)
            self.assertIsNotNone(agentic_rag)


if __name__ == "__main__":
    unittest.main()
