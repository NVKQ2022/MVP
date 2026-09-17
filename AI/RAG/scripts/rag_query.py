"""RAG: retrieve with all-MiniLM + generate with Azure OpenAI."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import API_KEY, CHROMA_COLLECTION, CHROMA_PERSIST_DIR, EMBEDDING_MODEL, ENDPOINT, MODEL_NAME
from embedding import EmbeddingService
from vectordb import VectorDB
from openai import OpenAI


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--persist-dir", type=Path, default=Path(CHROMA_PERSIST_DIR))
    p.add_argument("--collection", default=CHROMA_COLLECTION)
    args = p.parse_args()

    persist_dir = (PROJECT_ROOT / args.persist_dir).resolve() if not args.persist_dir.is_absolute() else args.persist_dir
    db = VectorDB(str(persist_dir), args.collection)
    embedder = EmbeddingService(model_name=EMBEDDING_MODEL)

    results = db.search(embedder.embed_text(args.query), top_k=args.top_k)
    context = "\n\n---\n\n".join([f"Source: {r['document']['source']}#{r['document']['chunk_id']}\n{r['document']['text']}" for r in results])
    print(f"retrieved {len(results)} chunks")

    client = OpenAI(api_key=API_KEY, base_url=ENDPOINT)
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Answer using the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {args.query}"},
        ],
        max_completion_tokens=500,
    )
    print(resp.choices[0].message.content)


if __name__ == "__main__":
    main()
