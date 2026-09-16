#!/usr/bin/env python3
"""
main.py
-------
Entry point for the To-Do List Manager CLI.

Design choice: all user-facing I/O (prompts, printing, input parsing) lives
here, separate from TaskManager's business logic. This "separation of
concerns" means the core logic could be reused behind a different interface
(e.g. a GUI or web API) without any changes.

The app supports two modes:
  1. Interactive menu mode (just run `python main.py`)
  2. One-shot command mode (e.g. `python main.py add "Buy milk"`)
     via argparse, for quick scripting/testing.
"""

import argparse
import sys

from storage import Storage
from task_manager import TaskManager

DEFAULT_FILE = "tasks.json"


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_tasks(tasks):
    """Print a list of tasks in a readable, aligned format."""
    if not tasks:
        print("  (no tasks to show)")
        return
    for task in tasks:
        print(f"  {task}")


def print_menu():
    print("\n===== To-Do List Manager =====")
    print("1. View all tasks")
    print("2. View pending tasks")
    print("3. View completed tasks")
    print("4. Add a task")
    print("5. Mark a task as completed")
    print("6. Mark a task as pending (undo)")
    print("7. Remove a task")
    print("8. Exit")


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def prompt_int(prompt_text):
    """
    Prompt the user for an integer, re-prompting on invalid input.
    Returns None if the user types nothing (cancel).
    """
    while True:
        raw = input(prompt_text).strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("  ⚠ Please enter a valid whole number (or leave blank to cancel).")


def prompt_nonempty(prompt_text):
    """Prompt for a non-empty string; re-prompt until given one or user cancels."""
    while True:
        raw = input(prompt_text).strip()
        if raw:
            return raw
        print("  ⚠ Input cannot be empty. Try again (Ctrl+C to cancel).")


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def run_interactive(manager):
    print("Welcome to your To-Do List Manager!")

    while True:
        print_menu()
        choice = input("Choose an option (1-8): ").strip()

        try:
            if choice == "1":
                print_tasks(manager.list_tasks("all"))

            elif choice == "2":
                print_tasks(manager.list_tasks("pending"))

            elif choice == "3":
                print_tasks(manager.list_tasks("completed"))

            elif choice == "4":
                description = prompt_nonempty("Task description: ")
                task = manager.add_task(description)
                print(f"  ✔ Added: {task}")

            elif choice == "5":
                task_id = prompt_int("Task ID to mark completed (blank to cancel): ")
                if task_id is None:
                    continue
                task = manager.complete_task(task_id)
                print(f"  ✔ Marked completed: {task}")

            elif choice == "6":
                task_id = prompt_int("Task ID to mark pending (blank to cancel): ")
                if task_id is None:
                    continue
                task = manager.uncomplete_task(task_id)
                print(f"  ↺ Marked pending: {task}")

            elif choice == "7":
                task_id = prompt_int("Task ID to remove (blank to cancel): ")
                if task_id is None:
                    continue
                confirm = input(f"  Remove task #{task_id}? (y/N): ").strip().lower()
                if confirm == "y":
                    task = manager.remove_task(task_id)
                    print(f"  ✔ Removed: {task}")
                else:
                    print("  Cancelled.")

            elif choice == "8":
                print("Goodbye!")
                break

            else:
                print("  ⚠ Invalid option. Please choose a number from 1 to 8.")

        # Expected/business errors: show a friendly message, keep the app running.
        except (ValueError, LookupError) as e:
            print(f"  ⚠ {e}")
        # Storage/IO errors: also non-fatal for the running session.
        except RuntimeError as e:
            print(f"  ⚠ Storage error: {e}")
        # Let the user cancel a prompt cleanly with Ctrl+C instead of a traceback.
        except KeyboardInterrupt:
            print("\n  Cancelled. Returning to menu.")


# ---------------------------------------------------------------------------
# One-shot command mode (argparse) — useful for scripting/quick tests
# ---------------------------------------------------------------------------

def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="A simple command-line To-Do List Manager."
    )
    parser.add_argument(
        "--file", default=DEFAULT_FILE,
        help=f"Path to the JSON storage file (default: {DEFAULT_FILE})"
    )
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("description", help="Task description")

    p_rm = sub.add_parser("remove", help="Remove a task by ID")
    p_rm.add_argument("task_id", type=int)

    p_done = sub.add_parser("complete", help="Mark a task as completed")
    p_done.add_argument("task_id", type=int)

    p_undo = sub.add_parser("uncomplete", help="Mark a task as pending")
    p_undo.add_argument("task_id", type=int)

    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument(
        "--status", choices=["all", "pending", "completed"], default="all"
    )

    return parser


def run_command(manager, args):
    """Run a single one-shot command based on parsed CLI args."""
    try:
        if args.command == "add":
            task = manager.add_task(args.description)
            print(f"Added: {task}")

        elif args.command == "remove":
            task = manager.remove_task(args.task_id)
            print(f"Removed: {task}")

        elif args.command == "complete":
            task = manager.complete_task(args.task_id)
            print(f"Marked completed: {task}")

        elif args.command == "uncomplete":
            task = manager.uncomplete_task(args.task_id)
            print(f"Marked pending: {task}")

        elif args.command == "list":
            print_tasks(manager.list_tasks(args.status))

        return 0

    except (ValueError, LookupError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Storage error: {e}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        storage = Storage(filepath=args.file)
        manager = TaskManager(storage)
    except RuntimeError as e:
        print(f"Fatal error loading tasks: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command:
        sys.exit(run_command(manager, args))
    else:
        run_interactive(manager)


if __name__ == "__main__":
    main()
