"""Test and verify the whole RAG pipeline using PolyRAG and the knowledge base."""

import sys
import logging
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("RAGTest")

from RAG.services.rag_engine import RAGEngine


def run_full_pipeline_verification():
    print("=" * 70)
    print("📁 STEP 1: VERIFY KNOWLEDGE BASE DOCUMENTS IN data/kb_documents/")
    print("=" * 70)
    kb_dir = Path("data/kb_documents")
    files = sorted(list(kb_dir.glob("*.txt")) + list(kb_dir.glob("*.md")))
    print(f"Found {len(files)} knowledge base documents:")
    for f in files[:4]:
        print(f"  • {f.name} ({f.stat().st_size} bytes)")
    print(f"  ... and {len(files) - 4} more.")

    print("\n" + "=" * 70)
    print("📦 STEP 2: INITIALIZE PolyRAG ENGINE & INGEST DOCUMENTS (Milvus Lite)")
    print("=" * 70)
    import shutil
    test_db = Path("data/milvus_pipeline_test.db")
    if test_db.exists():
        shutil.rmtree(test_db) if test_db.is_dir() else test_db.unlink()

    engine = RAGEngine(db_path=str(test_db), vector_store_type="milvus_lite")
    ingested_count = engine.ingest_kb_documents(docs_dir="data/kb_documents", force_regenerate=True)
    print(f"✅ Ingestion complete: {ingested_count} chunks indexed in Milvus Lite ({engine.vector_store.count()} total).")

    print("\n" + "=" * 70)
    print("🔍 STEP 3: TEST RETRIEVAL (Vector Similarity Search)")
    print("=" * 70)
    test_queries = [
        ("Query with Error Code", "Error Code: AUTH-401 / HTTP 401 token invalid"),
        ("Query without Error Code (Semantic)", "Customer account is locked out and cannot sign in"),
        ("Database Deadlock", "DB-DEADLOCK-001 transaction aborted"),
        ("File Upload Limit", "Uploaded file is too large FILE-413"),
    ]

    for label, query in test_queries:
        print(f"\n--- [{label}] ---")
        print(f"Query: \"{query}\"")
        results = engine.search(query, top_k=2)
        for idx, res in enumerate(results, 1):
            doc = res.get("document", {})
            score = res.get("score", 0.0)
            source = doc.get("source", "unknown")
            title = doc.get("title", "N/A")
            article_id = doc.get("article_id", "N/A")
            print(f"  Rank {idx} | Score: {score:.4f} | Source: {source} | ID: {article_id} | Title: {title}")

    print("\n" + "=" * 70)
    print("🤖 STEP 4: TEST NAIVE RAG GENERATION")
    print("=" * 70)
    q1 = "Customer sees 'Invalid or expired authentication token (AUTH-401)'. What are the troubleshooting steps?"
    print(f"Question: {q1}\n")
    response_naive = engine.query_naive(q1, top_k=2)
    print("Answer:")
    print(response_naive.answer)
    print(f"\nMetadata: Took {response_naive.took_ms}ms | Confidence: {response_naive.confidence} | LLM Calls: {response_naive.llm_calls}")

    print("\n" + "=" * 70)
    print("🧠 STEP 5: TEST ADVANCED RAG (Query Expansion + RRF Fusion)")
    print("=" * 70)
    q2 = "How do we resolve database deadlock errors?"
    print(f"Question: {q2}\n")
    response_adv = engine.query_advanced(q2, top_k=2, num_expanded_queries=2, verbose=True)
    print("\nAnswer:")
    print(response_adv.answer)
    print(f"\nSummary: {response_adv.reasoning_summary}")

    print("\n" + "=" * 70)
    print("✨ STEP 6: TEST AGENTIC RAG (Dynamic Planning & Multi-Round Loop)")
    print("=" * 70)
    q3 = "Customer reports account locked after failed logins."
    print(f"Question: {q3}\n")
    response_agent = engine.query_agentic(q3, top_k=2, max_rounds=2, verbose=True)
    print("\nAnswer:")
    print(response_agent.answer)
    print(f"\nSummary: {response_agent.reasoning_summary}")

    print("\n" + "=" * 70)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    # Cleanup temporary test database
    if test_db.exists():
        shutil.rmtree(test_db) if test_db.is_dir() else test_db.unlink()


if __name__ == "__main__":
    run_full_pipeline_verification()
