"""Execution timing utilities."""

import time
from contextlib import contextmanager
from typing import Generator, Dict, Any


@contextmanager
def timer_context() -> Generator[Dict[str, float], None, None]:
    """Context manager to measure execution duration in milliseconds.

    Example:
        with timer_context() as t:
            do_something()
        print(f"Elapsed: {t['elapsed_ms']:.2f} ms")
    """
    stats: Dict[str, float] = {"elapsed_ms": 0.0}
    start = time.perf_counter()
    try:
        yield stats
    finally:
        end = time.perf_counter()
        stats["elapsed_ms"] = round((end - start) * 1000.0, 2)
