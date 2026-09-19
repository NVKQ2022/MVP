from config import MODEL_NAME
from embedding import EmbeddingService
from vectordb import VectorDB


class RAGService:
    """Simple RAG Service that retrieves context from VectorDB and generates answers via LLM."""

    def __init__(
        self,
        client=None,
        embedding_service: EmbeddingService | None = None,
        vector_db: VectorDB | None = None,
        model_name: str = MODEL_NAME,
    ):
        # If any dependency is missing, load them from main.py runtime
        if client is None or embedding_service is None or vector_db is None:
            from main import build_runtime

            c, e, v = build_runtime()
            client = client or c
            embedding_service = embedding_service or e
            vector_db = vector_db or v

        self.client = client
        self.embedding_service = embedding_service
        self.vector_db = vector_db
        self.model_name = model_name

    def retrieve(self, query: str, top_k: int = 5):
        """Find the top-k most relevant chunks for a query."""
        query_vector = self.embedding_service.embed_text(query)
        return self.vector_db.search(query_vector, top_k=top_k)

    def format_context(self, search_results):
        """Format search results into a clean context string."""
        blocks = []
        for r in search_results:
            doc = r.get("document", {})
            source = doc.get("source", "unknown")
            chunk_id = doc.get("chunk_id", "")
            text = doc.get("text", "")
            blocks.append(f"Source: {source}#{chunk_id}\n{text}")
        return "\n\n---\n\n".join(blocks)

    def query(self, question: str, top_k: int = 5):
        """Perform end-to-end RAG: retrieve context and generate an answer."""
        results = self.retrieve(question, top_k=top_k)
        context = self.format_context(results)

        prompt = (
            f"Use the following context to answer the question. "
            f"If not in the context, say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\nAnswer:"
        )

        # Generate response using client (supports responses.create and chat.completions)
        if hasattr(self.client, "responses"):
            resp = self.client.responses.create(
                model=self.model_name,
                input=prompt,
            )
            answer = getattr(resp, "output_text", None)
            if not answer and hasattr(resp, "output") and resp.output:
                item = resp.output[0]
                answer = item.content[0].text if hasattr(item, "content") else str(item)
        else:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers using provided context."},
                    {"role": "user", "content": prompt},
                ],
            )
            answer = resp.choices[0].message.content

        return {
            "question": question,
            "answer": answer,
            "context": context,
            "sources": [r.get("document", {}) for r in results],
        }


if __name__ == "__main__":
    # Quick test when running python rag_service.py directly
    rag = RAGService()
    print("RAGService initialized successfully with dependencies from main.py!")
    print(f"Model: {rag.model_name}")
    print(f"Vector collection count: {rag.vector_db.count()}")
