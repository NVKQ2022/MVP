"""Tests for ReadingOrderSorter utility."""

from OCR.utils.ordering import ReadingOrderSorter
from OCR.services.base.base_ocr import RawOCRItem


def test_reading_order_sorter_multiline():
    """Tests that boxes from multiple lines and out-of-order columns are sorted correctly."""
    # Create boxes out of order:
    # Line 2, Word 2: (x=200, y=100)
    # Line 1, Word 2: (x=200, y=20)
    # Line 2, Word 1: (x=20,  y=100)
    # Line 1, Word 1: (x=20,  y=20)
    item_l2_w2 = RawOCRItem(text="World", confidence=0.9, polygon=[], box_2d=[200, 100, 280, 130])
    item_l1_w2 = RawOCRItem(text="Antigravity", confidence=0.9, polygon=[], box_2d=[200, 20, 320, 50])
    item_l2_w1 = RawOCRItem(text="Hello", confidence=0.9, polygon=[], box_2d=[20, 100, 100, 130])
    item_l1_w1 = RawOCRItem(text="Welcome", confidence=0.9, polygon=[], box_2d=[20, 20, 120, 50])

    unordered = [item_l2_w2, item_l1_w2, item_l2_w1, item_l1_w1]

    ordered = ReadingOrderSorter.sort(unordered)

    expected_texts = ["Welcome", "Antigravity", "Hello", "World"]
    result_texts = [item.text for item in ordered]

    assert result_texts == expected_texts


def test_reading_order_single_or_empty():
    """Tests that empty or single item lists are handled gracefully."""
    assert ReadingOrderSorter.sort([]) == []

    single = [RawOCRItem(text="Only", confidence=1.0, polygon=[], box_2d=[10, 10, 50, 30])]
    assert ReadingOrderSorter.sort(single) == single
