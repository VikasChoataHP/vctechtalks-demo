# Quickstart: Todo CLI

## Prerequisites

- Python 3.10 or newer.
- Run the commands from the project workspace root. The CLI stores `tasks.json` in its current working directory.

## Run the Tests

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Expected result: all storage and CLI acceptance tests pass using only the Python standard library.

## Try the CLI

Use a temporary working directory so the example does not change task data in the project directory:

```sh
PROJECT_ROOT="$PWD"
WORK_DIR="$(mktemp -d)"
cd "$WORK_DIR"
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli add "Write release notes"
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli list
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli complete 1
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli list
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli delete 1
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli list
```

Expected outcomes: the first command reports task 1 as pending; the first list shows it pending; after completion the next list shows it done; deletion succeeds; the final list reports `No tasks.`. Each command starts a new process, demonstrating persistence between invocations.

## Check Rejections

From the same temporary working directory:

```sh
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli add "   "
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli complete 0
PYTHONPATH="$PROJECT_ROOT/src" python3 -m todo_cli delete 999
```

Expected outcomes: each command exits non-zero and writes a clear error to stderr; rejected operations do not change `tasks.json`.

The task document format and validation rules are described in [data-model.md](data-model.md). The command/output contract is in [cli.md](../../contracts/cli.md).