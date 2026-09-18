# # embedding.py - Sentence-Transformers all-MiniLM
# from sentence_transformers import SentenceTransformer


# class EmbeddingService:
#     """Simple wrapper around all-MiniLM-L6-v2 (384 dims, cosine)."""

#     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
#         self.model_name = model_name
#         self.model = SentenceTransformer(model_name)
#         if hasattr(self.model, "get_embedding_dimension"):
#             self.dim = self.model.get_embedding_dimension()  # type: ignore
#         else:
#             self.dim = self.model.get_sentence_embedding_dimension()  # type: ignore

#     def embed_text(self, text: str) -> list[float]:
#         # normalize_embeddings=True -> cosine via dot product
#         return self.model.encode(text, normalize_embeddings=True).tolist()

#     def embed_batch(self, texts: list[str], batch_size: int = 128) -> list[list[float]]:
#         embs = self.model.encode(
#             texts,
#             batch_size=batch_size,
#             normalize_embeddings=True,
#             show_progress_bar=False,
#         )
#         return embs.tolist()





from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Interface for embedding implementations."""

    @property
    @abstractmethod
    def dim(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 128,
    ) -> list[list[float]]:
        raise NotImplementedError


class EmbeddingService:
    """
    Application-facing embedding service.

    Delegates the actual embedding work to the provided provider.
    """

    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    @property
    def dim(self) -> int:
        return self.provider.dim

    def embed_text(self, text: str) -> list[float]:
        return self.provider.embed_text(text)

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 128,
    ) -> list[list[float]]:
        return self.provider.embed_batch(
            texts,
            batch_size=batch_size,
        )


class HFEmbedding(EmbeddingProvider):
    """Hugging Face / Sentence-Transformers implementation."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

        self._dim = self.model.get_sentence_embedding_dimension()

    @property
    def dim(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(
            text,
            normalize_embeddings=True,
        ).tolist()

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 128,
    ) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI embedding implementation."""

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        import os
        from openai import OpenAI

        self.model_name = model_name

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        self._dim = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
        }.get(model_name)

        if self._dim is None:
            raise ValueError(
                f"Unsupported OpenAI embedding model: {model_name}"
            )

    @property
    def dim(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text,
        )

        return response.data[0].embedding

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 128,
    ) -> list[list[float]]:
        embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            response = self.client.embeddings.create(
                model=self.model_name,
                input=batch,
            )

            embeddings.extend(
                item.embedding
                for item in sorted(
                    response.data,
                    key=lambda item: item.index,
                )
            )

        return embeddings
