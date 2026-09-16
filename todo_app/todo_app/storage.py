"""
storage.py
----------
Handles all persistence: loading tasks from disk and saving them back.

Design choice: persistence is isolated in its own module/class so that
TaskManager (business logic) doesn't need to know *how* or *where* data is
stored. If we ever swapped JSON for SQLite, only this file would need to
change.
"""

import json
import os
from task import Task


class Storage:
    """Reads and writes a list of Task objects to a JSON file on disk."""

    def __init__(self, filepath="tasks.json"):
        self.filepath = filepath

    def load(self):
        """
        Load tasks from the JSON file.

        Returns an empty list if the file doesn't exist yet (first run) and
        raises a clear, user-friendly error if the file exists but is
        corrupted/unreadable, rather than letting a raw exception crash the app.
        """
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"The task file '{self.filepath}' is corrupted and could not "
                f"be parsed as JSON ({e}). Please fix or delete the file."
            )
        except OSError as e:
            raise RuntimeError(f"Could not read '{self.filepath}': {e}")

        try:
            return [Task.from_dict(item) for item in raw_data]
        except (KeyError, TypeError) as e:
            raise RuntimeError(
                f"The task file '{self.filepath}' has an unexpected format: {e}"
            )

    def save(self, tasks):
        """
        Save a list of Task objects to the JSON file.

        Writes to a temporary file first and then renames it into place.
        This "atomic write" pattern avoids leaving a half-written/corrupted
        tasks.json if the program is interrupted mid-write.
        """
        data = [task.to_dict() for task in tasks]
        tmp_path = self.filepath + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, self.filepath)
        except OSError as e:
            raise RuntimeError(f"Could not save tasks to '{self.filepath}': {e}")
