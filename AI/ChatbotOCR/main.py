"""Root entrypoint script for ChatbotOCR server and CLI tools."""

import sys
import argparse
from server.main import main as server_main
from OCR.cli import run_cli_ocr


def main():
    parser = argparse.ArgumentParser(description="ChatbotOCR unified server & CLI runner")
    parser.add_argument("--ocr-file", type=str, default=None, help="Run standalone OCR on an image file")
    parser.add_argument("--lang", type=str, default="en", help="OCR language code (default: en)")
    parser.add_argument("--save-annotated", type=str, default=None, help="Save annotated image output")
    parser.add_argument("--host", type=str, default=None, help="Server host bind address")
    parser.add_argument("--port", type=int, default=None, help="Server port number")
    parser.add_argument("--reload", action="store_true", help="Server development reload")

    args, _ = parser.parse_known_args()

    if args.ocr_file:
        run_cli_ocr(args.ocr_file, lang=args.lang, save_annotated=args.save_annotated)
    else:
        sys.argv = [sys.argv[0]]
        if args.host:
            sys.argv.extend(["--host", args.host])
        if args.port:
            sys.argv.extend(["--port", str(args.port)])
        if args.reload:
            sys.argv.append("--reload")
        server_main()


if __name__ == "__main__":
    main()
