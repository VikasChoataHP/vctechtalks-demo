"""Shared helpers: model client, chunking, embeddings, retrieval, and prompts."""

from __future__ import annotations

import json
import math
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

DATA_DIR = Path(__file__).parent / "data"

# Defaults point at local Ollama. Override with env vars to use a cloud free tier.
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("LLM_API_KEY", "ollama")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:7b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", CHAT_MODEL)

client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=180)

# Some embedding models were trained with task prefixes; skipping them hurts recall.
EMBED_PREFIXES: dict[str, tuple[str, str]] = {
    "nomic-embed-text": ("search_query: ", "search_document: "),
    "mxbai-embed-large": (
        "Represent this sentence for searching relevant passages: ",
        "",
    ),
}

STRICT_PROMPT = (
    "You are the Nimbus platform helpdesk assistant. Answer ONLY from the "
    "context below. If the context does not contain the answer, reply exactly: "
    '"I don\'t know based on the Nimbus docs." Keep answers short and cite the '
    "chunk ids you used in square brackets, like [deploy-guide#rollback]."
)


@dataclass
class Chunk:
    """One section of a doc: the unit we embed and retrieve."""

    id: str
    text: str


@dataclass
class GoldenItem:
    """One test question with the chunk that should be found and a reference answer."""

    question: str
    expected_chunk: str | None
    reference_answer: str


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_chunks() -> list[Chunk]:
    """Split every markdown doc into one chunk per '## ' section."""
    chunks: list[Chunk] = []
    for path in sorted((DATA_DIR / "docs").glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        doc_title = lines[0].lstrip("# ").strip()
        heading, body = "", []
        for line in [*lines[1:], "## "]:  # trailing sentinel flushes the last section
            if not line.startswith("## "):
                body.append(line)
                continue
            if heading:
                text = f"{doc_title} > {heading}\n" + "\n".join(body).strip()
                chunks.append(Chunk(id=f"{path.stem}#{slugify(heading)}", text=text))
            heading, body = line[3:].strip(), []
    return chunks


def load_golden() -> list[GoldenItem]:
    raw = json.loads((DATA_DIR / "golden.json").read_text(encoding="utf-8"))
    return [GoldenItem(**item) for item in raw]


def embed(
    texts: list[str], model: str, kind: str, use_prefix: bool = True
) -> list[list[float]]:
    """Embed texts as 'query' or 'document', adding the model's task prefix."""
    prefixes = EMBED_PREFIXES.get(model.split(":")[0], ("", ""))
    prefix = "" if not use_prefix else prefixes[0 if kind == "query" else 1]
    resp = client.embeddings.create(model=model, input=[prefix + t for t in texts])
    return [d.embedding for d in resp.data]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


class VectorIndex:
    """A tiny in-memory vector store. Fine for a demo, not for millions of chunks."""

    def __init__(
        self, chunks: list[Chunk], model: str = EMBED_MODEL, use_prefix: bool = True
    ) -> None:
        self.chunks, self.model, self.use_prefix = chunks, model, use_prefix
        start = time.perf_counter()
        self.vectors = embed([c.text for c in chunks], model, "document", use_prefix)
        self.build_seconds = time.perf_counter() - start
        self.dims = len(self.vectors[0])

    def search(self, query: str, k: int = 3) -> list[tuple[Chunk, float]]:
        [query_vec] = embed([query], self.model, "query", self.use_prefix)
        pairs = zip(self.chunks, self.vectors, strict=True)
        scored = [(c, cosine(query_vec, v)) for c, v in pairs]
        return sorted(scored, key=lambda pair: pair[1], reverse=True)[:k]

    def rank_of(self, query: str, chunk_id: str) -> int:
        """1-based position of chunk_id in the full ranking for this query."""
        ranked = [c.id for c, _ in self.search(query, k=len(self.chunks))]
        return ranked.index(chunk_id) + 1


def chat(messages: list[dict], model: str = CHAT_MODEL) -> str:
    resp = client.chat.completions.create(model=model, messages=messages, temperature=0)
    return (resp.choices[0].message.content or "").strip()


def format_context(hits: list[tuple[Chunk, float]]) -> str:
    return "\n\n".join(f"[{c.id}]\n{c.text}" for c, _ in hits)


def answer(
    question: str, hits: list[tuple[Chunk, float]], system_prompt: str = STRICT_PROMPT
) -> str:
    context = format_context(hits)
    return chat(
        [
            {"role": "system", "content": f"{system_prompt}\n\nCONTEXT:\n{context}"},
            {"role": "user", "content": question},
        ]
    )


def parse_json(text: str) -> dict | None:
    """Pull the first {...} block out of a model reply; small models add extra text."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
