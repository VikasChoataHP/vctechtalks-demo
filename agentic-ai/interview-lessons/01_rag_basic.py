"""Video 1: a basic RAG pipeline like the candidate built. It works, but is it good?"""

from __future__ import annotations

import argparse
import time

from common import CHAT_MODEL, EMBED_MODEL, VectorIndex, answer, load_chunks

DEFAULT_QUESTIONS = [
    "Can I push a new release to production on Saturday afternoon?",
    "How often do I have to change my service's API keys?",
    "What is the Wi-Fi password for the Gurugram office?",
]


def ask(index: VectorIndex, question: str, k: int) -> None:
    print("=" * 70)
    print(f"Q: {question}")
    start = time.perf_counter()
    hits = index.search(question, k=k)
    print("\nRetrieved:")
    for chunk, score in hits:
        print(f"  {score:.3f}  {chunk.id}")
    print(f"\nA: {answer(question, hits)}")
    print(f"\n({time.perf_counter() - start:.1f}s)\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?", help="ask your own question")
    parser.add_argument("-k", type=int, default=3, help="chunks to retrieve")
    args = parser.parse_args()

    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks. Embedding them with {EMBED_MODEL}...")
    index = VectorIndex(chunks)
    print(f"Index ready in {index.build_seconds:.1f}s, {index.dims} dimensions.")
    print(f"Answering with {CHAT_MODEL}.\n")

    for question in [args.question] if args.question else DEFAULT_QUESTIONS:
        ask(index, question, args.k)


if __name__ == "__main__":
    main()
