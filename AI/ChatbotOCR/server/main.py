import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import argparse
import uvicorn

from server.config import server_settings
from OCR.utils.logger import get_logger

logger = get_logger(__name__)


def run_server():
    """Starts the Uvicorn ASGI server."""
    logger.info(
        f"Starting {server_settings.app_name} on http://{server_settings.host}:{server_settings.port}"
    )
    uvicorn.run(
        "server.app:app",
        host=server_settings.host,
        port=server_settings.port,
        reload=server_settings.debug,
        log_level=server_settings.log_level.lower(),
    )


def main():
    parser = argparse.ArgumentParser(description="ChatbotOCR API Web Server")
    parser.add_argument(
        "--host", type=str, default=server_settings.host, help=f"Host address (default: {server_settings.host})"
    )
    parser.add_argument(
        "--port", type=int, default=server_settings.port, help=f"Port number (default: {server_settings.port})"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for local development"
    )

    args = parser.parse_args()

    if args.host:
        server_settings.host = args.host
    if args.port:
        server_settings.port = args.port
    if args.reload:
        server_settings.debug = True

    run_server()


if __name__ == "__main__":
    main()
