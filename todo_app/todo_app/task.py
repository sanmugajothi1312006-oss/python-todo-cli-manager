"""
task.py
-------
Defines the Task class: a single to-do item.

Design choice: Task is a plain data-holder (a small OOP class rather than a
dict) so that each task's shape is explicit and self-documenting. It also
knows how to serialize/deserialize itself to/from a dict, which keeps all
JSON-related knowledge about "what a task looks like" in one place instead
of scattered through storage.py.
"""

from datetime import datetime


class Task:
    """Represents a single to-do item."""

    def __init__(self, description, completed=False, created_at=None, task_id=None):
        self.task_id = task_id  # Assigned by TaskManager; None until added to a list
        self.description = description
        self.completed = completed
        # Store creation time as an ISO string so it's trivially JSON-serializable.
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")

    def mark_completed(self):
        """Flip this task's status to completed."""
        self.completed = True

    def mark_incomplete(self):
        """Flip this task's status back to not completed (undo)."""
        self.completed = False

    def to_dict(self):
        """Convert the Task into a plain dict, ready for JSON serialization."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Task object from a dict (e.g. loaded from JSON)."""
        return cls(
            description=data["description"],
            completed=data.get("completed", False),
            created_at=data.get("created_at"),
            task_id=data.get("task_id"),
        )

    def __str__(self):
        status = "✔" if self.completed else "✘"
        return f"[{status}] #{self.task_id}: {self.description}"
