# Quickstart: Validate the Todo CLI

## Prerequisites

- Python 3.10 or newer on `PATH`.
- Run application commands from the project directory; the default data file is `tasks.json` in the current working directory.

## Run Tests

From the repository root:

```sh
python3 --version
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Expected result: all unit and CLI tests pass without a database, network connection, or third-party package.

## Validate a Full CLI Session

From the project directory, run:

```sh
PYTHONPATH=src python3 -m todo_cli add "Write release notes"
PYTHONPATH=src python3 -m todo_cli list
PYTHONPATH=src python3 -m todo_cli complete 1
PYTHONPATH=src python3 -m todo_cli list
PYTHONPATH=src python3 -m todo_cli delete 1
PYTHONPATH=src python3 -m todo_cli list
```

Expected outcomes: add confirms a pending task and assigns its number; the first list shows it as pending; completing then listing shows it as done; deleting then listing reports `No tasks.`. Re-run `list` in a fresh process to verify persistence across restarts. These commands create or modify the project-local `tasks.json`.

## Validate Rejections

```sh
PYTHONPATH=src python3 -m todo_cli add "   "
PYTHONPATH=src python3 -m todo_cli complete 0
PYTHONPATH=src python3 -m todo_cli delete 999
```

Expected outcomes: each command reports an error on stderr and exits non-zero. The saved task document remains unchanged. For automated assertions, use temporary directories and compare the file before and after rejected operations.

See [contracts/cli.md](contracts/cli.md) for command and exit-status details, and [data-model.md](data-model.md) for the persistence format.