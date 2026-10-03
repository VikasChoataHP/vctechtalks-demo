# Data Model: Command-Line Todo Application

## Task

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Positive, unique within the task list, assigned monotonically, and stable for the lifetime of the task. |
| `description` | string | Trim leading/trailing whitespace on add; reject if empty after trimming; preserve internal spaces and punctuation. |
| `done` | boolean | `false` when created; set to `true` when completed. Completing an already-done task is idempotent. |

## Task List Document

The persisted `tasks.json` document has this shape:

```json
{
  "schema_version": 1,
  "next_id": 3,
  "tasks": [
    {"id": 1, "description": "Buy milk", "done": false},
    {"id": 2, "description": "Call Sam", "done": true}
  ]
}
```

`schema_version` is the integer format version. `next_id` is a positive integer greater than every current task ID, and is retained when the list is empty so deleted IDs are not reused. `tasks` is ordered by creation time; deleting a task does not renumber other tasks. IDs are the user-visible task numbers.

## Validation and State Changes

- Missing or zero-byte storage is interpreted as an empty list with `next_id` 1.
- A non-empty document must parse as JSON and match the supported schema. Reject unknown versions, wrong field types, duplicate/non-positive IDs, empty descriptions, invalid statuses, or a `next_id` that is not greater than every ID. Do not overwrite invalid data.
- Add trims the description, validates it, appends a pending task with `next_id`, then increments `next_id`.
- Complete accepts only a positive existing ID and changes `done` from `false` to `true`; a repeated completion leaves the state unchanged.
- Delete accepts only a positive existing ID and removes exactly that task. Other task IDs and statuses remain unchanged.
- List does not mutate storage and emits each task once with its ID, description, and pending/done status.
- Persist a mutation only after the complete new document has been serialized and atomically replaced. Any failure must leave the prior valid file in place and must not be reported as success.