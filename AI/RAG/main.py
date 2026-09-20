 
from openai import OpenAI

from chunking import ChunkingService, FixedSizeChunkingService
from config import (
    API_KEY,
    ENDPOINT,
    MODEL_NAME,
    PROVIDER,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
)
from embedding import (
    EmbeddingService,
    OpenAIEmbeddingService,
    HFEmbeddingService,
)
from rag_service import RAGService
from vectordb import VectorDB, ChromaVectorDB


def build_llm_client() -> OpenAI:
    return OpenAI(
        base_url=ENDPOINT,
        api_key=API_KEY,
    )


def build_chunking_service() -> ChunkingService:
    return FixedSizeChunkingService(
        chunk_size=300,
        overlap=30,
        drop_empty=True,
    )


def build_embedding_service() -> EmbeddingService:
    if PROVIDER == "openai":
        return OpenAIEmbeddingService(
            model_name=EMBEDDING_MODEL,
            base_url=ENDPOINT,
            api_key=API_KEY,
        )

    if PROVIDER == "hf":
        return HFEmbeddingService(
            model_name=EMBEDDING_MODEL,
        )

    raise ValueError(
        f"Unsupported embedding provider: {PROVIDER}"
    )


# def build_vector_db() -> VectorDB:
#     return ChromaVectorDB(
#         persist_directory=CHROMA_PERSIST_DIR,
#         collection_name=CHROMA_COLLECTION,
#     )


def build_vector_db(
    persist_directory: str | None = None,
    collection_name: str | None = None,
) -> VectorDB:
    return ChromaVectorDB(
        persist_directory=(
            persist_directory
            if persist_directory is not None
            else CHROMA_PERSIST_DIR
        ),
        collection_name=(
            collection_name
            if collection_name is not None
            else CHROMA_COLLECTION
        ),
    )



def build_rag_service() -> RAGService:
    client = build_llm_client()
    chunking_service = build_chunking_service()
    embedding_service = build_embedding_service()
    vector_db = build_vector_db()

    return RAGService(
        client=client,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        vector_db=vector_db,
        model_name=MODEL_NAME,
    )


def main():
    rag_service = build_rag_service()

    response = rag_service.query(
        "What is the capital of France?"
    )

    print(f"answer: {response['answer']}")


if __name__ == "__main__":
    main()
