# Project endpoint
# https://scyu-1027-resource.services.ai.azure.com/api/projects/scyu-1027

from embedding import EmbeddingService, OpenAIEmbedding, HFEmbedding
from chunking import ChunkingService
from config import API_KEY, ENDPOINT, MODEL_NAME, PROVIDER, CHROMA_PERSIST_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL

chunkingService = ChunkingService()


def build_runtime():
    from openai import OpenAI
    from vectordb import VectorDB

    client = OpenAI(
        base_url=ENDPOINT,
        api_key=API_KEY,
    )

    if PROVIDER == "openai":
        provider = OpenAIEmbedding(
            model_name=EMBEDDING_MODEL,
            base_url=ENDPOINT,
            api_key=API_KEY,
        )
    else:
        provider = HFEmbedding(model_name=EMBEDDING_MODEL)

    embeddingService = EmbeddingService(provider)
    vectorDB = VectorDB(
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION,
    )
    return client, embeddingService, vectorDB


def main():
    client, embeddingService, vectorDB = build_runtime()
    response = client.responses.create(
        model=MODEL_NAME,
        input="What is the capital of France?",
    )
    print(f"answer: {response.output[0]}")


if __name__ == "__main__":
    main()