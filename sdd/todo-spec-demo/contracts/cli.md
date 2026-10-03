# CLI Contract: Todo Application

Run commands from the project directory so the application reads and writes `tasks.json` there. Invoke the application as `python3 -m todo_cli` with `src` on `PYTHONPATH` during development.

## Commands

```text
python3 -m todo_cli add DESCRIPTION
python3 -m todo_cli list
python3 -m todo_cli complete TASK_NUMBER
python3 -m todo_cli delete TASK_NUMBER
```

- `add` accepts one description argument. Quote descriptions containing spaces. The application trims surrounding whitespace and rejects an empty result.
- `list` prints every task once, with its stable number, description, and `pending` or `done` status. An empty list prints `No tasks.`
- `complete` marks the matching task done. Completing a task that is already done succeeds without changing its description or creating a duplicate.
- `delete` removes exactly the task with the matching number. Other task numbers do not change.
- Task numbers are positive decimal integers assigned monotonically. Numbers are not reused after deletion.
- An unknown task number, invalid description, invalid number, or storage error is reported clearly; a rejected operation does not change saved tasks.

## Output and Exit Status

- Successful confirmations and task listings go to stdout.
- Usage, validation, and storage errors go to stderr. Errors must not claim an unsuccessful mutation was saved.
- Exit status `0` means the command succeeded (including listing an empty task list or completing an already-done task).
- Exit status `1` means a requested task does not exist or local task data could not be read or saved.
- Exit status `2` means command syntax or argument validation failed.

## Persistence

The only runtime data file is `tasks.json` in the current working directory. A missing or zero-byte file is an empty list. Malformed non-empty JSON or an unsupported schema is reported without replacing the file. Successful mutations replace the document atomically; see [data-model.md](../data-model.md) for its format and validation rules.