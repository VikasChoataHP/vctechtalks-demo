"""Video 4: what IS an AI agent? An LLM in a loop with tools, memory and a stop rule."""

from __future__ import annotations

import argparse
import json

from common import CHAT_MODEL, VectorIndex, client, load_chunks

DEFAULT_TASK = (
    "Users say payments are very slow. Check the payments-api status, find the "
    "right incident severity in our on-call policy, and open an incident ticket."
)

SYSTEM_PROMPT = (
    "You are an operations assistant for the Nimbus platform. Use the tools to "
    "find facts; never guess a policy, search the docs instead. Check the service "
    "status and the severity policy before creating a ticket. When you are done, "
    "reply with a short summary and no tool call."
)

# Fake live data so the demo works offline.
SERVICE_STATUS = {
    "payments-api": "DEGRADED: p95 latency 2.3s (normal 200ms) for all customers "
    "since 09:40 UTC",
    "orders-api": "HEALTHY",
    "search-api": "HEALTHY",
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the Nimbus platform docs (deploy, secrets, "
            "quotas, incidents/on-call, access, backups).",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_service_status",
            "description": "Get the live health status of a service.",
            "parameters": {
                "type": "object",
                "properties": {"service": {"type": "string"}},
                "required": ["service"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Open an incident ticket. This has a real side effect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "service": {"type": "string"},
                    "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
                },
                "required": ["title", "service", "severity"],
            },
        },
    },
]


class Tools:
    """The agent's 'hands'. The model only ever sees the strings these return."""

    def __init__(self, index: VectorIndex, auto_approve: bool) -> None:
        self.index, self.auto_approve = index, auto_approve

    def search_docs(self, query: str) -> str:
        return "\n\n".join(f"[{c.id}] {c.text}" for c, _ in self.index.search(query))

    def get_service_status(self, service: str) -> str:
        return SERVICE_STATUS.get(service, f"Unknown service '{service}'.")

    def create_ticket(self, title: str, service: str, severity: str) -> str:
        if not self.auto_approve:
            ask = (
                f"\n  !! Agent wants to open {severity} ticket '{title}'. Allow? [y/N] "
            )
            if input(ask).strip().lower() != "y":
                return "A human rejected this. Do not retry; summarise instead."
        ticket = {"ticket": "INC-1042", "severity": severity, "service": service}
        return json.dumps(ticket)

    def run(self, name: str, raw_args: str) -> str:
        if name not in {"search_docs", "get_service_status", "create_ticket"}:
            return f"Error: unknown tool '{name}'."
        try:
            return getattr(self, name)(**json.loads(raw_args or "{}"))
        except (json.JSONDecodeError, TypeError) as err:
            # Hand the error back so the model can correct itself on the next step.
            return f"Error: bad arguments for {name}: {err}"


def run_agent(task: str, tools: Tools, max_steps: int) -> None:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]
    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(
            model=CHAT_MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            print(f"\nStep {step}: DONE\n\n{msg.content}")
            return
        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            print(f"\nStep {step}: {call.function.name}({call.function.arguments})")
            result = tools.run(call.function.name, call.function.arguments)
            print(f"  <- {result[:160]}{'...' if len(result) > 160 else ''}")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )
    print(f"\nStopped: reached the {max_steps}-step limit without finishing.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", nargs="?", default=DEFAULT_TASK)
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="skip the human approval before create_ticket",
    )
    args = parser.parse_args()

    print(f"Model: {CHAT_MODEL}\nTask:  {args.task}")
    tools = Tools(VectorIndex(load_chunks()), args.auto_approve)
    run_agent(args.task, tools, args.max_steps)


if __name__ == "__main__":
    main()
