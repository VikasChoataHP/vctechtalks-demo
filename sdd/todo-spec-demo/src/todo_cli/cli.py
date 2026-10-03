import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from .storage import TaskStorageError, load_tasks, save_tasks


CommandHandler = Callable[[argparse.Namespace], int]


def _positive_task_number(value: str) -> int:
    try:
        task_number = int(value, 10)
    except ValueError as error:
        raise argparse.ArgumentTypeError("task number must be a positive integer") from error
    if task_number < 1:
        raise argparse.ArgumentTypeError("task number must be a positive integer")
    return task_number


def _add(arguments: argparse.Namespace) -> int:
    path = _task_file()
    task_list = load_tasks(path)
    task = task_list.add(arguments.description)
    save_tasks(path, task_list)
    print(f"Added task {task.id}: {task.description} (pending)")
    return 0


def _list(_arguments: argparse.Namespace) -> int:
    task_list = load_tasks(_task_file())
    if not task_list.tasks:
        print("No tasks.")
        return 0

    for task in task_list.tasks:
        status = "done" if task.done else "pending"
        print(f"{task.id}. [{status}] {task.description}")
    return 0


def _complete(arguments: argparse.Namespace) -> int:
    path = _task_file()
    task_list = load_tasks(path)
    task = task_list.complete(arguments.task_number)
    save_tasks(path, task_list)
    print(f"Completed task {task.id}: {task.description} (done)")
    return 0


def _delete(arguments: argparse.Namespace) -> int:
    path = _task_file()
    task_list = load_tasks(path)
    task = task_list.delete(arguments.task_number)
    save_tasks(path, task_list)
    print(f"Deleted task {task.id}: {task.description}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo")
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="add a task")
    add_parser.add_argument("description", help="short task description")
    add_parser.set_defaults(handler=_add)

    list_parser = commands.add_parser("list", help="list all tasks")
    list_parser.set_defaults(handler=_list)

    for command_name in ("complete", "delete"):
        command_parser = commands.add_parser(command_name, help=f"{command_name} a task")
        command_parser.add_argument("task_number", type=_positive_task_number)
        handler = _complete if command_name == "complete" else _delete
        command_parser.set_defaults(handler=handler)

    return parser


def _task_file() -> Path:
    return Path.cwd() / "tasks.json"


def main(arguments: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    parsed_arguments: argparse.Namespace = parser.parse_args(arguments)
    handler: CommandHandler = parsed_arguments.handler

    try:
        return handler(parsed_arguments)
    except TaskStorageError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except LookupError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2