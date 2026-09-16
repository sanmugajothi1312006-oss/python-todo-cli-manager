# To-Do List Manager (CLI)

A simple, dependency-free command-line To-Do List application written in
Python, using object-oriented design and JSON file persistence.

---

## 1. Features

- Add tasks
- Remove tasks
- View tasks (all / pending / completed)
- Mark tasks as completed (and undo)
- Data persists between runs in a local `tasks.json` file
- Robust input validation and error handling — bad input never crashes the app
- Two ways to use it: an interactive menu, or one-shot commands for scripting

---

## 2. Requirements

- Python 3.7+
- **No external dependencies** — only the Python standard library
  (`json`, `argparse`, `os`, `datetime`, `unittest`) is used.

---

## 3. Project Structure

```
todo_app/
├── .github/
│   └── workflows/
│       └── tests.yml        # CI: runs the test suite on every push/PR
├── .gitignore                # Excludes tasks.json, caches, venvs, etc.
├── LICENSE                   # MIT License
├── requirements.txt           # No deps — present for standard tooling
├── main.py                   # CLI entry point: menus, argparse, input handling
├── task.py                    # Task class (a single to-do item)
├── task_manager.py             # TaskManager class (core business logic)
├── storage.py                  # Storage class (JSON load/save persistence)
├── tests/
│   ├── __init__.py             # Makes tests/ an importable package
│   └── test_task_manager.py     # Automated unit tests
├── tasks.json                  # Created automatically on first run (git-ignored)
└── README.md
```

### Why this structure? (Design Rationale)

The app is split into four layers, each with one job — a common
separation-of-concerns pattern that keeps the code easy to test and extend:

| Module          | Responsibility                                                   |
|------------------|-------------------------------------------------------------------|
| `task.py`        | Defines *what a task is* (data + simple behavior like `mark_completed`) |
| `storage.py`     | Defines *how tasks are saved/loaded* (JSON file I/O only)        |
| `task_manager.py`| Defines *the business rules* (add/remove/list/complete, ID assignment, validation) |
| `main.py`        | Defines *how the user interacts* (menu, prompts, argparse, printing) |

Because `TaskManager` only depends on an abstract `Storage` object (passed
in via its constructor — "dependency injection"), you could later swap
`storage.py` for a SQLite-backed version without touching business logic or
the CLI at all. It also means `TaskManager` can be unit-tested using a
temporary file, with no need to mock the CLI.

---

## 4. Application Flow (Pseudocode)

```
START
  Load tasks.json into memory (or start empty if file doesn't exist)
  IF a subcommand was passed on the command line (add/remove/list/...):
      Run that single command, print result, exit
  ELSE:
      LOOP forever (interactive menu):
          Show menu: [View all | View pending | View completed |
                      Add | Complete | Uncomplete | Remove | Exit]
          Read user's choice
          TRY:
              Dispatch to the matching TaskManager operation
              Print a friendly confirmation / result
          CATCH ValueError (bad input) or LookupError (task not found):
              Print a friendly warning, stay in the loop
          CATCH RuntimeError (disk/storage problem):
              Print a friendly warning, stay in the loop
          IF choice == Exit: break loop
END
```

Each mutating operation (add/remove/complete/uncomplete) immediately saves
the full task list back to `tasks.json`, so no data is lost if the program
is closed unexpectedly.

### Task lifecycle (state diagram)

```
   add_task()
       │
       ▼
  [ Pending ] ── complete_task() ──▶ [ Completed ]
       ▲                                   │
       └────────── uncomplete_task() ──────┘

  (from any state) ── remove_task() ──▶ [ Deleted ]
```

---

## 5. Installation

No installation needed beyond Python itself — the project uses only the
standard library.

### Option A: Clone from GitHub

```bash
git clone https://github.com/<your-username>/todo-list-manager.git
cd todo-list-manager

# (Optional but good practice) use a virtual environment
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# There's nothing to install, but this is here for tooling that expects it
pip install -r requirements.txt

python3 --version   # should be 3.7 or higher
```

### Option B: Extract from the ZIP archive

```bash
unzip todo_app.zip
cd todo_app
python3 --version   # should be 3.7 or higher
```

---

## 6. How to Run

### A) Interactive mode (recommended for normal use)

```bash
python3 main.py
```

You'll see a numbered menu:

```
===== To-Do List Manager =====
1. View all tasks
2. View pending tasks
3. View completed tasks
4. Add a task
5. Mark a task as completed
6. Mark a task as pending (undo)
7. Remove a task
8. Exit
Choose an option (1-8):
```

Type a number and press Enter. Follow the prompts. Pressing **Ctrl+C** at
any input prompt cancels that action and returns you to the menu instead of
crashing.

### B) One-shot command mode (useful for quick tests/scripts)

```bash
python3 main.py add "Buy groceries"
python3 main.py add "Finish report"
python3 main.py list
python3 main.py complete 1
python3 main.py list --status pending
python3 main.py remove 2
```

### Using a custom data file

By default tasks are saved to `tasks.json` in the current directory. To use
a different file (e.g. to keep separate lists):

```bash
python3 main.py --file work_tasks.json add "Review PR"
```

---

## 7. Design Decisions

- **Object-Oriented Core**: `Task` and `TaskManager` are classes because a
  to-do app naturally models *things* (tasks) and *an owner of those things*
  (the manager) with clear behavior — this maps more cleanly to OOP than a
  purely functional style would, while `main.py` still uses plain functions
  for the stateless UI logic.
- **JSON for storage**: human-readable, needs no external database, and
  Python's `json` module is in the standard library — keeping the project
  dependency-free.
- **Atomic writes**: `storage.py` writes to a temporary file and renames it
  into place, so a crash or power loss mid-save can't leave `tasks.json`
  half-written/corrupted.
- **IDs based on max-seen, not list position**: task IDs are assigned
  incrementally and never reused, even after deletions, so a task ID always
  refers to one specific task for its whole life.
- **Errors as exceptions, caught at the UI boundary**: `TaskManager` raises
  plain `ValueError` (bad input, e.g. empty description) and `LookupError`
  (task ID not found). `main.py` is the only place that catches and
  displays them — this keeps the business logic UI-agnostic and easy to
  reuse.
- **Two run modes**: the interactive menu is friendliest for a human; the
  `argparse` subcommands make the app scriptable and easy to test from a
  shell without needing to simulate `input()`.

---

## 8. Error Handling Summary

| Situation                                   | Behavior                                                |
|----------------------------------------------|----------------------------------------------------------|
| Empty/blank task description                 | Rejected with a clear message; user is re-prompted (interactive) or gets a non-zero exit code (command mode) |
| Non-numeric task ID entered                   | Rejected with a message; re-prompted, no crash            |
| Task ID that doesn't exist                    | `LookupError` caught and shown as a friendly warning       |
| `tasks.json` missing                          | Treated as "no tasks yet" — app starts with an empty list |
| `tasks.json` corrupted / invalid JSON          | Clear error message on startup, explaining the problem    |
| Disk write failure (e.g. permissions)          | Caught as `RuntimeError`, reported without crashing the running session |
| Ctrl+C during a prompt                        | Cancels that one action, returns to the menu              |

---

## 9. Testing

### A) Automated tests

Unit tests use Python's built-in `unittest` (no extra install needed):

```bash
python3 -m unittest tests/test_task_manager.py -v
```

This covers: adding tasks, rejecting empty descriptions, completing tasks,
completing a non-existent task (error case), removing tasks, removing a
non-existent task (error case), filtering by pending/completed, data
persisting across separate `TaskManager` instances (simulating an app
restart), and ID uniqueness after deletion.

### B) Manual test scenarios

Try these in interactive mode (`python3 main.py`) to verify behavior:

1. **Happy path**: Add 3 tasks → View all tasks → mark task #2 completed →
   View pending tasks (should show only #1 and #3) → View completed tasks
   (should show only #2).
2. **Empty description**: Choose "Add a task" and press Enter without
   typing anything → should re-prompt instead of accepting an empty task.
3. **Invalid ID format**: Choose "Mark a task as completed" and type `abc`
   → should show a validation warning and re-prompt.
4. **Non-existent ID**: Choose "Remove a task" and enter an ID that doesn't
   exist (e.g. `999`) → should show "No task found with ID 999." without
   crashing.
5. **Cancel with blank input**: At any ID prompt, press Enter with nothing
   typed → should cancel and return to the menu.
6. **Persistence**: Add a task, exit the app (`8`), then re-run
   `python3 main.py` — the task should still be there.
7. **Undo completion**: Complete a task, then use option 6 to mark it
   pending again — it should move back to the pending list.
8. **Corrupted file recovery check**: Manually edit `tasks.json` to contain
   invalid JSON (e.g. delete a closing bracket) and re-run the app — it
   should print a clear error explaining the file is corrupted, rather than
   an unreadable Python traceback.

---

## 10. Continuous Integration

A GitHub Actions workflow (`.github/workflows/tests.yml`) runs the full
unit test suite automatically on every push and pull request against
`main`, across Python 3.8, 3.10, and 3.12, so regressions are caught
before merge. No setup is required — it runs as soon as the repo is
pushed to GitHub.

---

## 11. Possible Future Enhancements

(Not implemented — listed to show awareness of extensibility)

- Due dates and priority levels
- Sorting/searching tasks by keyword
- Categories/tags
- Colorized terminal output
