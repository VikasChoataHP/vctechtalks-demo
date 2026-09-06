
# Exercise 01 — Todo CLI App (used in Video 2 & Video 3)

## Exact `/specify` prompt (Video 2)
```
/specify Build a command-line Todo application for a single user.
The user can:
- Add a new task with a short text description
- List all tasks, showing which are done and which are pending
- Mark a task as done by its number
- Delete a task by its number
Tasks must be saved so they still exist after closing and reopening the app.
This is for personal use on one computer, no login or multi-user support needed.
```

## What to check after `/specify` runs (talk through this on camera)
- A new spec file is generated (usually under a `specs/` folder). Open it and read it out loud to viewers.
- Point out: no mention of Python/JavaScript/database yet — that's intentional, spec stage is about WHAT, not HOW.
- If Spec Kit's `/clarify` command asks questions (e.g., "should tasks have due dates?"), answer live on camera — this is great, authentic content. Suggested answers to keep it simple:
  - Due dates? "No, keep it simple for now — just text and done/not-done status."
  - Storage format? "Your choice, whatever is simplest — a local file is fine."

## Exact `/plan` prompt (Video 3)
```
/plan Use Python 3 for the CLI. Store tasks in a local JSON file called tasks.json
in the project folder. No external database, no web server — this is a pure
command-line tool run with `python todo.py`.
```

## Exact `/tasks` prompt (Video 3)
```
/tasks
```
(No extra text needed — Spec Kit reads the plan and spec automatically and generates a task checklist.)

## Exact `/implement` prompt (Video 3)
```
/implement
```

## Manual test script (Video 3)
```
python todo.py add "Buy milk"
python todo.py add "Finish YouTube script"
python todo.py list
python todo.py done 1
python todo.py list
python todo.py delete 2
python todo.py list
```
Expected: after `done 1`, "Buy milk" shows as completed. After `delete 2`, "Finish YouTube script" is gone. Closing and reopening the terminal and running `python todo.py list` again should still show saved tasks (proves the JSON file storage works).

## Common issues to expect live (mention these, they make good "real debugging" content)
- If `python` command isn't found, try `python3` instead (very common on Mac/Linux).
- If Copilot asks for confirmation before running terminal commands, that's normal — approve it, explain to viewers that Copilot always asks before running anything on their machine (safety feature).
- If `tasks.json` isn't created in the expected folder, check the terminal's current directory with `pwd` (Mac/Linux) or `cd` (Windows) — a classic beginner gotcha, good teaching moment.