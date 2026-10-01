"""CLI runner for direct OCR processing on images."""

import argparse
import sys
import cv2

from OCR.services.orchestrator.ocr_orchestrator import OCROrchestratorService
from OCR.services.codec.image_codec import ImageCodecService
from OCR.config import settings
from OCR.utils.logger import get_logger

logger = get_logger(__name__)


def run_cli_ocr(image_path: str, lang: str = "en", save_annotated: str = None):
    """Runs OCR directly on a local image file via the Domain Orchestrator."""
    orchestrator = OCROrchestratorService()
    print(f"\n📄 Processing image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image from '{image_path}'")
        sys.exit(1)

    response = orchestrator.process_image(
        payload=image,
        lang=lang,
        return_annotated_image=bool(save_annotated),
    )

    print("\n" + "=" * 50)
    print(f"✅ OCR COMPLETED in {response.metadata.processing_time_ms:.1f}ms")
    print(f"📊 Total lines detected: {response.total_lines}")
    print("=" * 50)
    print("\n📝 EXTRACTED TEXT:\n")
    print(response.full_text)
    print("\n" + "=" * 50)

    if save_annotated and response.annotated_image_base64:
        annotated_img = ImageCodecService.decode(response.annotated_image_base64)
        cv2.imwrite(save_annotated, annotated_img)
        print(f"🖼️ Saved visual annotation to: {save_annotated}")


def main():
    parser = argparse.ArgumentParser(description="Standalone OCR Command Line Interface")
    parser.add_argument("file", type=str, help="Path to image file to process")
    parser.add_argument(
        "--lang", type=str, default=settings.ocr_default_lang, help=f"Language code (default: {settings.ocr_default_lang})"
    )
    parser.add_argument(
        "--save-annotated", type=str, default=None, help="Path to save annotated output image"
    )

    args = parser.parse_args()
    run_cli_ocr(args.file, lang=args.lang, save_annotated=args.save_annotated)


if __name__ == "__main__":
    main()
