"""Entrypoint for 20-Question Evaluation Benchmark."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.application.use_cases.evaluate_benchmark import DEFAULT_BENCHMARK_QUESTIONS
from src.presentation.cli.run_benchmark import main

BENCHMARK_QUESTIONS = DEFAULT_BENCHMARK_QUESTIONS

if __name__ == "__main__":
    main()
