"""Tests for OCROrchestratorService."""

from OCR.services.codec.image_codec import ImageCodecService


def test_orchestrator_process_image(mock_orchestrator, sample_image):
    """Tests orchestrator execution with Base64 payload and confidence filtering."""
    b64_str = ImageCodecService.encode_base64(sample_image)

    response = mock_orchestrator.process_image(
        payload=b64_str,
        min_confidence=0.5,
        return_annotated_image=True,
    )

    assert response.success is True
    assert response.total_lines == 4
    assert "Invoice #1024" in response.full_text
    assert "Total: $495.00" in response.full_text
    assert response.annotated_image_base64 is not None
    assert response.annotated_image_base64.startswith("data:image/jpeg;base64,")
    assert response.metadata.image_width == sample_image.shape[1]
    assert response.metadata.image_height == sample_image.shape[0]
    assert response.metadata.processing_time_ms >= 0


def test_orchestrator_confidence_filtering(mock_orchestrator, sample_image):
    """Tests that high confidence threshold filters out items."""
    response = mock_orchestrator.process_image(
        payload=sample_image,
        min_confidence=0.999,  # Higher than mock confidence 0.98
    )

    assert response.success is True
    assert response.total_lines == 0
    assert response.full_text == ""


def test_orchestrator_get_service_info(mock_orchestrator):
    """Tests metadata reporting."""
    info = mock_orchestrator.get_service_info()
    assert info.active_backend == "MockOCR"
    assert "paddle" in info.available_backends
    assert "mock" in info.available_backends
