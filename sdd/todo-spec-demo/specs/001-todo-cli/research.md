# Research: Command-Line Todo Application

## Python CLI and Dependencies

- **Decision**: Use Python 3.10+ and the standard library, with `argparse` for `add`, `list`, `complete`, and `delete` commands.
- **Rationale**: The feature is a small offline CLI and needs no external framework. Python 3.10+ is the implementation baseline; `argparse` provides conventional usage and argument errors.
- **Alternatives considered**: A custom parser adds maintenance. Third-party CLI frameworks are unnecessary for four commands.

## Persistence Format and Validation

- **Decision**: Store a versioned JSON object containing `schema_version`, `next_id`, and a `tasks` array. Each task has a positive integer `id`, trimmed non-empty `description`, and boolean `done` field. A missing or zero-byte file represents an empty task list. Reject malformed non-empty JSON, unsupported schema versions, and invalid records with an error; never silently overwrite unreadable data.
- **Rationale**: This format is inspectable, validates identity and status explicitly, and leaves room for deliberate future migrations. The spec explicitly treats empty saved data as an empty list.
- **Alternatives considered**: A bare array cannot preserve the next ID after all tasks are deleted. JSON Schema or a validation package would add an unnecessary dependency. Resetting corrupt data risks data loss.

## Task Identity

- **Decision**: Use a monotonically increasing positive integer ID as the user-visible task number. Persist `next_id`, increment it on add, and never reuse IDs after deletion; gaps are expected.
- **Rationale**: Existing task numbers remain stable and a deleted task's number cannot unexpectedly refer to a different task.
- **Alternatives considered**: Compacting list positions after deletion is permitted by the spec but changes identifiers and can confuse subsequent selections.

## Safe File Updates

- **Decision**: Validate an operation and build the complete new state before writing. Serialize to a temporary file in the same directory, flush the write, and replace `tasks.json` with `os.replace`. Clean up an uncommitted temporary file and report I/O failures to stderr with a non-zero exit status.
- **Rationale**: Same-directory replacement avoids exposing a partially written JSON document during ordinary interrupted writes. The command only reports success after replacement succeeds.
- **Alternatives considered**: Direct writes can truncate the only copy on failure. A database is expressly out of scope. File locking is not included because concurrent invocations are outside the single-user requirements.

## Tests

- **Decision**: Use `unittest`, temporary directories, and subprocess tests. Inject a storage path for tests so they do not touch the project data file.
- **Rationale**: Standard-library tests avoid runtime/test dependencies while checking both the storage boundary and observable CLI contract.
- **Alternatives considered**: `pytest` is convenient but introduces an extra dependency. Unit-only tests would not verify argument parsing, output streams, or exit codes.

## Resolved Assumptions

- The default data path is `tasks.json` in the current working directory; users run the CLI from the project directory. This makes the requested project-local file location explicit and allows isolated CLI tests in temporary working directories.
- An empty file is treated as an empty task list, while malformed non-empty JSON is an error.
- Concurrent CLI processes are unsupported; no locking protocol is planned.
- Runtime task data is local personal data and should not be committed. The project should ignore the generated `tasks.json` file.