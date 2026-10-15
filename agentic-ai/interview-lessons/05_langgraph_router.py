"""Video 5: a LangGraph workflow with nodes, conditional edges and a retry loop."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from common import STRICT_PROMPT, VectorIndex, chat, load_chunks, parse_json

MAX_REWRITES = 2
ROUTES = ("out_of_scope", "chitchat", "docs")

DEFAULT_QUESTIONS = [
    "Can I deploy to prod on Saturday?",
    "Hey, good morning! How are you?",
    "Who won the cricket match yesterday?",
    "how long r the old db copies kept around",
]

CLASSIFY_PROMPT = """Classify the message for a Nimbus platform helpdesk bot.
- docs: a question about deploying, secrets, quotas, incidents or on-call,
  access, or database backups
- chitchat: greetings or small talk
- out_of_scope: anything else
Reply with exactly one word: docs, chitchat or out_of_scope.

MESSAGE: {question}"""

GRADE_PROMPT = """Do these documents contain the information needed to answer
the question?

QUESTION: {question}

DOCUMENTS:
{docs}

Reply with JSON only: {{"relevant": true or false}}"""

REWRITE_PROMPT = """Rewrite this question so it is easier to search in platform
docs. Use clear, formal wording. Reply with the rewritten question only.

QUESTION: {question}"""


class State(TypedDict, total=False):
    question: str
    route: str
    query: str
    docs: str
    relevant: bool
    attempts: int
    answer: str


def classify(state: State) -> State:
    reply = chat([{"role": "user", "content": CLASSIFY_PROMPT.format(**state)}]).lower()
    route = next((r for r in ROUTES if r in reply), "docs")
    return {"route": route, "query": state["question"], "attempts": 0}


def retrieve(state: State, index: VectorIndex) -> State:
    hits = index.search(state["query"], k=3)
    return {"docs": "\n\n".join(f"[{c.id}] {c.text}" for c, _ in hits)}


def grade(state: State) -> State:
    reply = chat([{"role": "user", "content": GRADE_PROMPT.format(**state)}])
    verdict = parse_json(reply) or {}
    return {"relevant": bool(verdict.get("relevant", False))}


def rewrite(state: State) -> State:
    query = chat([{"role": "user", "content": REWRITE_PROMPT.format(**state)}])
    return {"query": query, "attempts": state["attempts"] + 1}


def generate(state: State) -> State:
    system = f"{STRICT_PROMPT}\n\nCONTEXT:\n{state['docs']}"
    reply = chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": state["question"]},
        ]
    )
    return {"answer": reply}


def chitchat(state: State) -> State:
    system = "You are a friendly Nimbus platform helpdesk bot. Reply in one sentence."
    reply = chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": state["question"]},
        ]
    )
    return {"answer": reply}


def refuse(state: State) -> State:
    return {
        "answer": "Sorry, I can only help with the Nimbus platform docs, "
        "and I couldn't find this there."
    }


def route_after_classify(state: State) -> str:
    return state["route"]


def route_after_grade(state: State) -> str:
    if state["relevant"]:
        return "generate"
    return "rewrite" if state["attempts"] < MAX_REWRITES else "refuse"


def build_graph(index: VectorIndex) -> CompiledStateGraph:
    graph = StateGraph(State)
    graph.add_node("classify", classify)
    graph.add_node("retrieve", lambda state: retrieve(state, index))
    graph.add_node("grade", grade)
    graph.add_node("rewrite", rewrite)
    graph.add_node("generate", generate)
    graph.add_node("chitchat", chitchat)
    graph.add_node("refuse", refuse)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {"docs": "retrieve", "chitchat": "chitchat", "out_of_scope": "refuse"},
    )
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges(
        "grade",
        route_after_grade,
        {"generate": "generate", "rewrite": "rewrite", "refuse": "refuse"},
    )
    graph.add_edge("rewrite", "retrieve")
    for node in ("generate", "chitchat", "refuse"):
        graph.add_edge(node, END)
    return graph.compile()


def show(node: str, update: State) -> None:
    detail = {k: v for k, v in update.items() if k not in ("docs", "answer")}
    print(f"  -> {node:<9} {detail if detail else ''}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?", help="ask your own question")
    parser.add_argument(
        "--show-graph",
        action="store_true",
        help="print the graph as Mermaid and save graph.md",
    )
    args = parser.parse_args()

    app = build_graph(VectorIndex(load_chunks()))
    if args.show_graph:
        mermaid = app.get_graph().draw_mermaid()
        Path("graph.md").write_text(f"```mermaid\n{mermaid}\n```\n", encoding="utf-8")
        print(mermaid + "\nSaved to graph.md (paste into https://mermaid.live)\n")

    for question in [args.question] if args.question else DEFAULT_QUESTIONS:
        print("=" * 70 + f"\nQ: {question}")
        final = ""
        for event in app.stream({"question": question}, stream_mode="updates"):
            for node, update in event.items():
                show(node, update)
                final = update.get("answer", final)
        print(f"\nA: {final}\n")


if __name__ == "__main__":
    main()
