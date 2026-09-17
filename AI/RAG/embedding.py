# embedding.py - Sentence-Transformers all-MiniLM
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Simple wrapper around all-MiniLM-L6-v2 (384 dims, cosine)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        if hasattr(self.model, "get_embedding_dimension"):
            self.dim = self.model.get_embedding_dimension()  # type: ignore
        else:
            self.dim = self.model.get_sentence_embedding_dimension()  # type: ignore

    def embed_text(self, text: str) -> list[float]:
        # normalize_embeddings=True -> cosine via dot product
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: list[str], batch_size: int = 128) -> list[list[float]]:
        embs = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embs.tolist()
