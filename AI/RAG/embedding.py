
from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    """
    Abstract interface for embedding implementations.
    """

    @property
    @abstractmethod
    def dim(self) -> int:
        """
        Return the dimensionality of the embedding vector.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 128,
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """
        raise NotImplementedError


class HFEmbeddingService(EmbeddingService):
    """
    Hugging Face / Sentence-Transformers embedding implementation.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

        dimension = self.model.get_sentence_embedding_dimension()

        if dimension is None:
            raise ValueError(
                f"Could not determine embedding dimension "
                f"for model: {model_name}"
            )

        self._dim = dimension

    @property
    def dim(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> list[float]:
        """
        Generate a normalized embedding for a single text.
        """
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 128,
    ) -> list[list[float]]:
        """
        Generate normalized embeddings for multiple texts.
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()


class OpenAIEmbeddingService(EmbeddingService):
    """
    OpenAI-compatible embedding implementation.
    """

    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
    }

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        from openai import OpenAI

        if model_name not in self.MODEL_DIMENSIONS:
            raise ValueError(
                f"Unsupported embedding model: {model_name}"
            )

        self.model_name = model_name
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        self._dim = self.MODEL_DIMENSIONS[model_name]

    @property
    def dim(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text.
        """
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
        """
        Generate embeddings for multiple texts.

        The input is split into batches to avoid sending
        excessively large requests.
        """
        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        embeddings: list[list[float]] = []

        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]

            response = self.client.embeddings.create(
                model=self.model_name,
                input=batch,
            )

            batch_embeddings = sorted(
                response.data,
                key=lambda item: item.index,
            )

            embeddings.extend(
                item.embedding
                for item in batch_embeddings
            )

        return embeddings

