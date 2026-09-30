"""Use case for document ingestion into vector database."""

from pathlib import Path
from typing import Any

from src.domain.entities.document import Document
from src.domain.interfaces.chunker import ChunkerInterface
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.domain.interfaces.vector_store import VectorStoreInterface


class IngestDocumentsUseCase:
    """Chunks documents, generates embeddings, and stores them in vector store."""

    def __init__(
        self,
        chunker: ChunkerInterface,
        embedding_model: EmbeddingModelInterface,
        vector_store: VectorStoreInterface,
    ) -> None:
        self.chunker = chunker
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def ingest_text(
        self,
        text: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Chunk, embed, and store a document in the vector store.

        Args:
            text: Document text to ingest.
            source: Source filename or identifier.
            metadata: Additional metadata dictionary.

        Returns:
            List of ingested document records.
        """
        if not text.strip():
            return []

        chunks = self.chunker.chunk(text)
        if not chunks:
            return []

        vectors = self.embedding_model.embed_batch(chunks)

        documents: list[dict[str, Any]] = []
        for chunk_id, chunk_text in enumerate(chunks):
            doc = {
                "text": chunk_text,
                "source": source,
                "chunk_id": chunk_id,
            }
            if metadata:
                doc.update(metadata)
            documents.append(doc)

        self.vector_store.add_documents(
            vectors=vectors,
            documents=documents,
        )

        return documents

    def ingest_file(
        self,
        file_path: Path | str,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Read and ingest a text file."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        text = path.read_text(encoding="utf-8", errors="ignore")
        return self.ingest_text(
            text=text,
            source=path.name,
            metadata=metadata,
        )
