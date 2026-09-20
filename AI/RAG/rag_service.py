
from typing import Any

from config import MODEL_NAME
from chunking import ChunkingService
from embedding import EmbeddingService
from vectordb import VectorDB


class RAGService:
    """RAG service for document ingestion, retrieval, and generation."""

    def __init__(
        self,
        client,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        vector_db: VectorDB,
        model_name: str = MODEL_NAME,
    ):
        self.client = client
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.vector_db = vector_db
        self.model_name = model_name

    def ingest(
        self,
        text: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Chunk, embed, and store a document in the vector database.

        Args:
            text: Document text to ingest.
            source: Original document source/path/name.
            metadata: Optional metadata attached to every chunk.

        Returns:
            The documents that were added to the vector database.
        """
        if not text.strip():
            return []

        chunks = self.chunking_service.chunk(text)

        if not chunks:
            return []

        vectors = self.embedding_service.embed_batch(chunks)

        documents = []

        for chunk_id, chunk in enumerate(chunks):
            document = {
                "text": chunk,
                "source": source,
                "chunk_id": chunk_id,
            }

            if metadata:
                document.update(metadata)

            documents.append(document)

        self.vector_db.add_documents(
            vectors=vectors,
            documents=documents,
        )

        return documents

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Find the top-k most relevant chunks for a query."""
        query_vector = self.embedding_service.embed_text(query)

        return self.vector_db.search(
            query_vector,
            top_k=top_k,
        )

    def format_context(
        self,
        search_results: list[dict[str, Any]],
    ) -> str:
        """Format search results into a clean context string."""
        blocks = []

        for result in search_results:
            document = result.get("document", {})

            source = document.get("source", "unknown")
            chunk_id = document.get("chunk_id", "")
            text = document.get("text", "")

            blocks.append(
                f"Source: {source}#{chunk_id}\n{text}"
            )

        return "\n\n---\n\n".join(blocks)

    def query(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Perform end-to-end RAG: retrieve context and generate an answer."""
        results = self.retrieve(
            question,
            top_k=top_k,
        )

        context = self.format_context(results)

        prompt = (
            "Use the following context to answer the question. "
            "If the answer is not in the context, say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

        response = self.client.responses.create(
            model=self.model_name,
            input=prompt,
        )

        answer = response.output_text

        return {
            "question": question,
            "answer": answer,
            "context": context,
            "sources": [
                result.get("document", {})
                for result in results
            ],
        }
