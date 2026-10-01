"""Unified CLI and Server Launcher for ChatbotOCR."""

import sys
import argparse
from pathlib import Path

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def run_diagnose_cli(image_path: str, pipeline: str = "naive", top_k: int = 2) -> None:
    """Run full end-to-end diagnosis directly from the terminal."""
    from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService
    from RAG.services.rag_engine import RAGEngine

    path = Path(image_path)
    if not path.exists():
        print(f"❌ Error: Image file '{image_path}' not found.")
        sys.exit(1)

    print("=" * 65)
    print(f"🔍 STEP 1: Running OCR on '{path.name}'...")
    print("=" * 65)
    ocr = OCROrchestratorService()
    img_bytes = path.read_bytes()
    ocr_res = ocr.process_image(payload=img_bytes, min_confidence=0.4, sort_reading_order=True)

    print("\n📝 Recognized OCR Text:")
    print("─" * 65)
    print(ocr_res.full_text)
    print("─" * 65)

    print("\n" + "=" * 65)
    print(f"📚 STEP 2: Querying PolyRAG Knowledge Base ({pipeline.upper()})...")
    print("=" * 65)
    rag = RAGEngine()
    if rag.vector_store.count() == 0:
        rag.ingest_kb_documents()

    prompt = f"Customer screenshot error text:\n{ocr_res.full_text}\n\nProvide troubleshooting steps."
    if pipeline == "advanced":
        rag_res = rag.query_advanced(prompt, top_k=top_k)
    elif pipeline == "agentic":
        rag_res = rag.query_agentic(prompt, top_k=top_k)
    else:
        rag_res = rag.query_naive(prompt, top_k=top_k)

    print("\n🤖 Grounded Support Resolution:")
    print("─" * 65)
    print(rag_res.answer)
    print("─" * 65)
    print("\n📖 Retrieved Sources:")
    for s in rag_res.sources:
        src = s.get("source", "N/A")
        title = s.get("title", "")
        print(f"  • {src} — {title}")
    print(f"\n⏱ Latency: {rag_res.took_ms}ms | Confidence: {rag_res.confidence}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ChatbotOCR: Unified Optical Character Recognition & Support RAG Platform",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. Server Subcommand
    server_parser = subparsers.add_parser("server", help="Start the FastAPI REST server")
    server_parser.add_argument("--host", type=str, default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    server_parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code change")

    # 2. Diagnose Subcommand (End-to-End Image -> RAG)
    diag_parser = subparsers.add_parser("diagnose", help="Diagnose a screenshot end-to-end (OCR + PolyRAG)")
    diag_parser.add_argument("image_path", type=str, help="Path to error screenshot image (PNG, JPG)")
    diag_parser.add_argument("-p", "--pipeline", choices=["naive", "advanced", "agentic"], default="naive")
    diag_parser.add_argument("-k", "--top-k", type=int, default=2)

    # 3. OCR Standalone Subcommand
    ocr_parser = subparsers.add_parser("ocr", help="Run standalone OCR recognition on an image")
    ocr_parser.add_argument("image_path", type=str, help="Path to image file")
    ocr_parser.add_argument("--lang", type=str, default="en", help="Language code (default: en)")
    ocr_parser.add_argument("--save-annotated", type=str, default=None, help="Save annotated visualization image")

    # 4. RAG Standalone Subcommand
    rag_parser = subparsers.add_parser("rag", help="Query or chat with the PolyRAG knowledge base")
    rag_parser.add_argument("-q", "--query", type=str, default=None, help="Question to ask")
    rag_parser.add_argument("-i", "--interactive", action="store_true", help="Launch interactive chat session")
    rag_parser.add_argument("-p", "--pipeline", choices=["naive", "advanced", "agentic"], default="naive")
    rag_parser.add_argument("-k", "--top-k", type=int, default=2)
    rag_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose reasoning output")

    args = parser.parse_args()

    # Default to server if no arguments passed
    if args.command is None or args.command == "server":
        from server.main import main as server_main
        host = getattr(args, "host", "0.0.0.0")
        port = getattr(args, "port", 8000)
        reload_flag = getattr(args, "reload", False)
        sys.argv = [sys.argv[0], "--host", host, "--port", str(port)]
        if reload_flag:
            sys.argv.append("--reload")
        server_main()

    elif args.command == "diagnose":
        run_diagnose_cli(args.image_path, pipeline=args.pipeline, top_k=args.top_k)

    elif args.command == "ocr":
        from OCR.cli import run_cli_ocr
        run_cli_ocr(args.image_path, lang=args.lang, save_annotated=args.save_annotated)

    elif args.command == "rag":
        from RAG.cli import main as rag_main
        sys.argv = [sys.argv[0]]
        if args.query:
            sys.argv.extend(["-q", args.query])
        if args.interactive:
            sys.argv.append("-i")
        sys.argv.extend(["-p", args.pipeline, "-k", str(args.top_k)])
        if args.verbose:
            sys.argv.append("-v")
        rag_main()


if __name__ == "__main__":
    main()
