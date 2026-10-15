"""Video 2: which embedding model, and WHY? Measure it on your own data."""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, field

import openai

from common import VectorIndex, load_chunks, load_golden

# (label, model, use_prefix). The "no prefix" row shows a common silent mistake.
DEFAULT_CONFIGS = [
    ("all-minilm", "all-minilm", True),
    ("nomic-embed-text (no prefix)", "nomic-embed-text", False),
    ("nomic-embed-text", "nomic-embed-text", True),
    ("mxbai-embed-large", "mxbai-embed-large", True),
]


@dataclass
class Result:
    label: str
    dims: int
    index_seconds: float
    query_ms: float
    ranks: list[int] = field(default_factory=list)
    misses: list[tuple[str, int]] = field(default_factory=list)

    def hit_at(self, k: int) -> float:
        return sum(r <= k for r in self.ranks) / len(self.ranks)

    @property
    def mrr(self) -> float:
        return sum(1 / r for r in self.ranks) / len(self.ranks)


def evaluate(label: str, model: str, use_prefix: bool) -> Result:
    index = VectorIndex(load_chunks(), model=model, use_prefix=use_prefix)
    golden = [g for g in load_golden() if g.expected_chunk]
    result = Result(label, index.dims, index.build_seconds, 0.0)
    start = time.perf_counter()
    for item in golden:
        rank = index.rank_of(item.question, item.expected_chunk)
        result.ranks.append(rank)
        if rank > 1:
            result.misses.append((item.question, rank))
    result.query_ms = (time.perf_counter() - start) * 1000 / len(golden)
    return result


def print_table(results: list[Result]) -> None:
    print(
        f"\n{'Model':<30}{'Dims':>6}{'Index s':>9}{'Query ms':>10}"
        f"{'Hit@1':>8}{'Hit@3':>8}{'MRR':>7}"
    )
    print("-" * 78)
    for r in results:
        print(
            f"{r.label:<30}{r.dims:>6}{r.index_seconds:>9.1f}{r.query_ms:>10.0f}"
            f"{r.hit_at(1):>8.0%}{r.hit_at(3):>8.0%}{r.mrr:>7.2f}"
        )


def print_misses(results: list[Result]) -> None:
    print("\nWhere the right chunk was NOT ranked #1:")
    for r in results:
        print(f"\n  {r.label}")
        for question, rank in r.misses or [("(none, every answer was #1)", 1)]:
            rank_text = f"rank {rank:>2}" if rank > 1 else "       "
            print(f"    {rank_text}  {question}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", help="override the models to compare")
    args = parser.parse_args()
    configs = [(m, m, True) for m in args.models] if args.models else DEFAULT_CONFIGS

    results = []
    for label, model, use_prefix in configs:
        print(f"Evaluating {label}...")
        try:
            results.append(evaluate(label, model, use_prefix))
        except openai.APIStatusError as err:
            print(f"  skipped ({err.status_code}). Is it pulled? ollama pull {model}")
    if results:
        print_table(results)
        print_misses(results)


if __name__ == "__main__":
    main()
