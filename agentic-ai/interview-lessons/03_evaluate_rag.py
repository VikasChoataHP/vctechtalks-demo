"""Video 3: how do you KNOW your RAG works? Retrieval metrics + LLM-as-judge."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

from common import (
    EMBED_MODEL,
    JUDGE_MODEL,
    STRICT_PROMPT,
    GoldenItem,
    VectorIndex,
    answer,
    chat,
    format_context,
    load_chunks,
    load_golden,
    parse_json,
)

SLOPPY_PROMPT = (
    "You are a friendly, confident helpdesk assistant. Always give the user a "
    "complete and helpful answer. Use the context below if it helps."
)

WEAK_EMBED_MODEL = os.getenv("WEAK_EMBED_MODEL", "all-minilm")

CONFIGS = {
    "good": {"embed": EMBED_MODEL, "k": 3, "prompt": STRICT_PROMPT},
    "sloppy-prompt": {"embed": EMBED_MODEL, "k": 3, "prompt": SLOPPY_PROMPT},
    "weak-retrieval": {"embed": WEAK_EMBED_MODEL, "k": 1, "prompt": STRICT_PROMPT},
}

FAITHFULNESS_JUDGE = """You are a strict evaluator.
Is every factual claim in the ANSWER supported by the CONTEXT?
Saying "I don't know" counts as faithful.

CONTEXT:
{context}

ANSWER:
{answer}

Reply with JSON only: {{"faithful": true or false, "reason": "<one short sentence>"}}"""

CORRECTNESS_JUDGE = """You are a strict evaluator.
Does the CANDIDATE answer give the same key facts as the REFERENCE answer?
Extra harmless detail is fine. If the REFERENCE says the assistant should not know,
the CANDIDATE is correct only if it clearly says it does not know.

QUESTION: {question}
REFERENCE: {reference}
CANDIDATE: {answer}

Reply with JSON only: {{"correct": true or false, "reason": "<one short sentence>"}}"""


@dataclass
class Row:
    question: str
    retrieval_hit: bool | None  # None when no chunk is expected (out-of-scope)
    faithful: bool
    correct: bool
    answer: str
    reasons: str


def judge(prompt: str, key: str) -> tuple[bool, str]:
    reply = chat([{"role": "user", "content": prompt}], model=JUDGE_MODEL)
    verdict = parse_json(reply)
    if verdict is None or key not in verdict:
        return False, f"judge reply was not valid JSON: {reply[:80]!r}"
    return bool(verdict[key]), str(verdict.get("reason", ""))


def evaluate_item(index: VectorIndex, item: GoldenItem, k: int, prompt: str) -> Row:
    hits = index.search(item.question, k=k)
    ids = [c.id for c, _ in hits]
    hit = None if item.expected_chunk is None else item.expected_chunk in ids
    reply = answer(item.question, hits, prompt)
    faithful, why_f = judge(
        FAITHFULNESS_JUDGE.format(context=format_context(hits), answer=reply),
        "faithful",
    )
    correct, why_c = judge(
        CORRECTNESS_JUDGE.format(
            question=item.question, reference=item.reference_answer, answer=reply
        ),
        "correct",
    )
    return Row(item.question, hit, faithful, correct, reply, f"{why_f} | {why_c}")


def mark(value: bool | None) -> str:
    return " - " if value is None else (" ✓ " if value else " ✗ ")


def run_config(name: str) -> list[Row]:
    cfg = CONFIGS[name]
    print(f"\n### Config: {name}  (embed={cfg['embed']}, k={cfg['k']})")
    index = VectorIndex(load_chunks(), model=cfg["embed"])
    print(f"{'Retr':>5}{'Faith':>6}{'Corr':>6}  Question")
    rows = []
    for item in load_golden():
        row = evaluate_item(index, item, cfg["k"], cfg["prompt"])
        print(
            f"{mark(row.retrieval_hit):>5}{mark(row.faithful):>6}"
            f"{mark(row.correct):>6}  {row.question}"
        )
        rows.append(row)
    return rows


def summarize(name: str, rows: list[Row]) -> None:
    retrieval = [r.retrieval_hit for r in rows if r.retrieval_hit is not None]
    print(
        f"\n{name}: retrieval hit rate {sum(retrieval) / len(retrieval):.0%}, "
        f"faithfulness {sum(r.faithful for r in rows) / len(rows):.0%}, "
        f"correctness {sum(r.correct for r in rows) / len(rows):.0%}"
    )
    for r in rows:
        if not (r.faithful and r.correct):
            print(
                f"\n  ✗ {r.question}\n    answer: {r.answer[:200]}\n"
                f"    judge:  {r.reasons}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        choices=CONFIGS,
        action="append",
        help="config(s) to run; default runs all of them",
    )
    args = parser.parse_args()
    print(f"Judge model: {JUDGE_MODEL}")
    for name in args.config or list(CONFIGS):
        summarize(name, run_config(name))


if __name__ == "__main__":
    main()
