# Tasks: Command-Line Todo Application

**Input**: Design documents in `/specs/001-todo-cli/` (`plan.md`, `spec.md`, `research.md`, `data-model.md`)

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`

**Tests**: The specification defines independent acceptance tests and measurable success criteria. Implement the specified scenarios with Python's standard-library `unittest`; no third-party test dependencies are needed.

**Organization**: Tasks are grouped by user story. All three stories are P1 in the specification.

**Implementation paths**: Python package in `src/todo_cli/`; tests in `tests/`; the data file is `tasks.json` in the current project working directory.

## Phase 1: Setup

**Purpose**: Create the package/test layout and keep local task data out of version control.

- [X] T001 Create the package scaffold with `src/todo_cli/__init__.py`, `src/todo_cli/__main__.py`, and the `tests/` directory.
- [X] T002 [P] Add `tasks.json` to the repository-root `.gitignore` so personal runtime data is not committed.

---

## Phase 2: Foundational

**Purpose**: Implement the shared task representation, persistence boundary, and CLI startup that all stories require.

- [X] T003 Define the `Task` and `TaskList` representations, JSON field validation, and stable positive ID rules in `src/todo_cli/model.py`.
- [X] T004 Implement loading and saving the versioned JSON document, including missing/zero-byte handling, invalid-data errors, and same-directory atomic replacement in `src/todo_cli/storage.py`.
- [X] T005 Implement the shared `argparse` entry point, current-working-directory `tasks.json` selection, and stdout/stderr plus exit-status handling in `src/todo_cli/cli.py` and `src/todo_cli/__main__.py`.
- [X] T006 [P] Add storage tests for missing and empty files, valid round trips, malformed/unsupported documents, and failed atomic replacement preserving the prior file in `tests/test_storage.py`.

**Checkpoint**: The package starts, task data can be validated and persisted, and the storage boundary is covered independently.

---

## Phase 3: User Story 1 - Capture a Task (Priority: P1, MVP)

**Goal**: Add a trimmed, non-empty description as a pending task with the next stable number and persist it across invocations.

**Independent Test**: In an empty temporary working directory, add a valid description, confirm the assigned number and pending status, run the CLI again and confirm the task remains; verify whitespace-only input fails and leaves saved data unchanged.

- [X] T007 [P] [US1] Add CLI acceptance tests for valid add, number/status confirmation, persistence across invocations, and whitespace-only rejection without data changes in `tests/test_cli.py`.
- [X] T008 [P] [US1] Implement `TaskList.add` to trim and validate descriptions, assign `next_id`, create a pending task, and advance the ID counter in `src/todo_cli/model.py`.
- [X] T009 [US1] Implement the `add` command handler to persist the new task and report its number and pending status only after a successful save in `src/todo_cli/cli.py`.

**Checkpoint**: A user can add a valid task and retrieve it after a fresh CLI invocation; rejected descriptions do not mutate storage.

---

## Phase 4: User Story 2 - Review Task Status (Priority: P1)

**Goal**: List every current task once with its stable number, description, and clear pending/done status, or report an empty list.

**Independent Test**: Seed persisted pending and done tasks, run `list`, and verify each appears exactly once with the right status; run against missing/empty storage and verify an empty-list message without a fabricated entry.

- [X] T010 [P] [US2] Add CLI acceptance tests for pending/done listing, empty-list output, and listing persisted data in `tests/test_cli.py`.
- [X] T011 [P] [US2] Implement the `list` command to read saved tasks and print each number, description, and unambiguous status, or `No tasks.` when empty, in `src/todo_cli/cli.py`.

**Checkpoint**: Listing reflects saved state, distinguishes both statuses, and handles an empty list clearly.

---

## Phase 5: User Story 3 - Complete and Remove Tasks (Priority: P1)

**Goal**: Complete or delete a task by its number while preserving other tasks and rejecting malformed or unknown selections.

**Independent Test**: Start with two persisted tasks, complete one, verify its done status, delete the other, and verify the result after a fresh invocation. Confirm repeated completion is harmless and invalid numbers leave saved data unchanged.

- [X] T012 [P] [US3] Add CLI acceptance tests for completion, idempotent repeated completion, deletion, malformed/unknown selections, and preservation of unaffected tasks in `tests/test_cli.py`.
- [X] T013 [P] [US3] Implement `TaskList.complete` and `TaskList.delete` so only the selected task changes or is removed and IDs of remaining tasks stay stable in `src/todo_cli/model.py`.
- [X] T014 [US3] Implement `complete` and `delete` command handlers with positive-integer parsing, unknown-task errors, persistence, and success confirmation in `src/todo_cli/cli.py`.

**Checkpoint**: Completing and deleting by number work across restarts; invalid selections do not alter saved tasks.

---

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Restore the runnable guide referenced by the plan and validate the complete CLI workflow.

- [X] T015 Write the runnable setup, test, add/list/complete/delete, and rejection scenarios with expected results in `specs/001-todo-cli/quickstart.md`.
- [X] T016 Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` and execute the scenarios in `specs/001-todo-cli/quickstart.md`; fix any failures in the corresponding `src/todo_cli/` or `tests/` files.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T001 and T002 can run in parallel.
- **Foundational (Phase 2)**: Starts after setup. T003 precedes T004; after T004, T005 and T006 can run in parallel. The whole phase blocks user-story work.
- **User Stories (Phases 3-5)**: All require the foundation. Story work is staged US1 → US2 → US3 because the implementation and acceptance tests share `model.py`, `cli.py`, and `tests/test_cli.py`.
- **Polish (Phase 6)**: Run after the desired stories; T016 depends on the quickstart and all implementation/test tasks.

### User Story Dependencies

- **US1 (P1)**: Depends on the foundational task model, storage, and CLI startup; no behavioral dependency on another story.
- **US2 (P1)**: Depends only on the foundation. Its independent test can seed pending and done records directly; it does not require the add command to have been implemented.
- **US3 (P1)**: Depends only on the foundation. Its independent test can seed tasks directly; it does not require list behavior, though it is staged after US2 to avoid conflicting edits to shared files.

### Dependency Graph

```text
Setup (T001, T002)
  -> Foundation (T003 -> T004 -> [T005, T006])
  -> US1 (T007 || T008 -> T009)
  -> US2 (T010 || T011)
  -> US3 (T012 || T013 -> T014)
  -> Polish (T015 -> T016)
```

`||` marks tasks that can proceed in parallel; arrows indicate prerequisites or safe execution order.

### Parallel Opportunities

- T001 and T002 touch separate paths and can run in parallel.
- After T004, T005 and T006 touch separate files and can run in parallel.
- Within each story, acceptance-test authoring and model/command work marked `[P]` target different files and can proceed in parallel; the command handler task follows the model operation where applicable.
- User-story phases are staged to avoid conflicting edits to shared files, not because their user-visible behavior is inherently dependent.

## Parallel Example: User Story 1

```text
T007: Add acceptance coverage in tests/test_cli.py
T008: Implement TaskList.add in src/todo_cli/model.py
After both: T009 wires add behavior in src/todo_cli/cli.py
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1 only, then validate add, persistence across invocations, and whitespace rejection.
3. Deliver the capture workflow as the MVP; proceed with listing and lifecycle actions afterward.

### Incremental Delivery

1. Add US2 and validate saved pending/done output and the empty-list case.
2. Add US3 and validate complete/delete persistence, idempotency, and invalid-selection behavior.
3. Complete the quickstart and run the full standard-library test suite.

## Independent Test Criteria

- **US1**: A valid description is trimmed, assigned the next number, reported pending, and remains after a fresh process; whitespace-only input fails without changing the data file.
- **US2**: Seed pending and done tasks and verify each appears exactly once with number, description, and status; empty storage reports no tasks.
- **US3**: Complete and delete selected tasks, verify changes after a fresh process, repeat completion harmlessly, and verify invalid selections leave the stored document unchanged.