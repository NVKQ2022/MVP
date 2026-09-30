"""CLI Runner for 20-Question Benchmark Evaluation."""

import argparse
from src.container import default_container


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 20-Question evaluation comparing Naive RAG vs Agentic RAG.")
    parser.add_argument("--top-k", type=int, default=3, help="Top-K chunks for retrieval")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions to evaluate")
    args = parser.parse_args()

    benchmark_use_case = default_container.build_benchmark_use_case()
    summary = benchmark_use_case.execute(top_k=args.top_k, limit=args.limit)

    print("\n" + "=" * 70)
    print("                 BENCHMARK EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total Evaluated Questions : {summary['total_questions']}")
    print(f"Naive RAG Accuracy       : {summary['naive_hits']}/{summary['total_questions']} ({summary['naive_accuracy']}%)")
    print(f"Agentic RAG Accuracy     : {summary['agentic_hits']}/{summary['total_questions']} ({summary['agentic_accuracy']}%)")
    print(f"Accuracy Gain            : +{summary['improvement']}%")
    print(f"Avg Naive Latency        : {summary['avg_naive_latency_ms']} ms")
    print(f"Avg Agentic Latency      : {summary['avg_agentic_latency_ms']} ms")
    print("=" * 70)


if __name__ == "__main__":
    main()
