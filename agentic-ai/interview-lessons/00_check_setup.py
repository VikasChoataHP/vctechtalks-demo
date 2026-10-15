"""Video 0: check that your free AI setup works before you start the series."""

from __future__ import annotations

import sys
import time

import openai

from common import BASE_URL, CHAT_MODEL, EMBED_MODEL, client, embed

OPTIONAL_MODELS = ["all-minilm", "mxbai-embed-large"]


def with_tag(name: str) -> str:
    return name if ":" in name else f"{name}:latest"


def check_ollama_models() -> None:
    installed = {m.id for m in client.models.list()}
    for name in [CHAT_MODEL, EMBED_MODEL, *OPTIONAL_MODELS]:
        needed = "required" if name in (CHAT_MODEL, EMBED_MODEL) else "for video 2"
        mark = "OK " if with_tag(name) in installed else "MISSING"
        hint = "" if mark == "OK " else f"  ->  ollama pull {name}"
        print(f"  [{mark}] {name} ({needed}){hint}")


def main() -> int:
    print(f"Endpoint:    {BASE_URL}")
    print(f"Chat model:  {CHAT_MODEL}")
    print(f"Embed model: {EMBED_MODEL}\n")
    try:
        if "11434" in BASE_URL:
            print("Models pulled in Ollama:")
            check_ollama_models()
            print()

        start = time.perf_counter()
        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": "Reply with one word: ready"}],
            temperature=0,
        )
        reply = (resp.choices[0].message.content or "").strip()
        print(f"Chat test:   '{reply}' in {time.perf_counter() - start:.1f}s")

        start = time.perf_counter()
        [vector] = embed(["hello world"], EMBED_MODEL, "document")
        seconds = time.perf_counter() - start
        print(f"Embed test:  {len(vector)} dimensions in {seconds:.1f}s")
    except openai.APIConnectionError:
        print("Cannot reach the model server. Is Ollama running? Open the app or run:")
        print("  ollama serve")
        return 1
    except openai.APIStatusError as err:
        print(f"The server returned an error ({err.status_code}): {err.message}")
        print("Check the model name, or pull it first with: ollama pull <model>")
        return 1

    print("\nAll good. You're ready for the series!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
