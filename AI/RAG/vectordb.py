"""Simple Chroma VectorDB."""

import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings


class VectorDB:
    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "rfc_docs"):
        from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION

        # env overrides
        if persist_directory == "chroma_db" and CHROMA_PERSIST_DIR:
            persist_directory = CHROMA_PERSIST_DIR
        if collection_name == "rfc_docs" and CHROMA_COLLECTION:
            collection_name = CHROMA_COLLECTION

        self.persist_directory = persist_directory
        self.collection_name = collection_name
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )

    def clear(self):
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, vectors, documents, batch_size: int = 5000):
        """Add pre-computed vectors + documents {text, source, chunk_id}."""
        if not documents:
            return
        texts = [d["text"] for d in documents]
        metadatas = [{k: v for k, v in d.items() if k != "text"} for d in documents]
        ids = [f"{Path(d['source']).stem}_{d['chunk_id']}_{uuid.uuid4().hex[:8]}" for d in documents]

        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i : i + batch_size],
                documents=texts[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
                embeddings=vectors[i : i + batch_size],
            )

    def search(self, query_vector, top_k: int = 5):
        res = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        out = []
        if not res["ids"] or not res["ids"][0]:
            return out
        for _id, doc, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]):
            out.append(
                {
                    "score": 1 - float(dist),  # cosine similarity
                    "distance": float(dist),
                    "document": {"_id": _id, "text": doc, **(meta or {})},
                }
            )
        return out

    def count(self):
        return self.collection.count()

    def peek(self, limit=5):
        return self.collection.peek(limit)
