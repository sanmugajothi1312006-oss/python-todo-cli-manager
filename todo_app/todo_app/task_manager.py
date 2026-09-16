"""
task_manager.py
----------------
Core business logic of the To-Do List Manager.

Design choice: TaskManager is the single "source of truth" for task state
during a run. It owns the in-memory list of Task objects, assigns IDs, and
delegates persistence to a Storage instance (dependency injection), which
makes this class easy to unit-test with a fake/mock storage if desired.
"""

from task import Task


class TaskManager:
    """Manages a collection of Task objects: add, remove, list, complete."""

    def __init__(self, storage):
        self.storage = storage
        self.tasks = self.storage.load()
        # Track the next ID to hand out. Based on the max existing ID so
        # IDs stay unique even after tasks have been removed in past runs.
        self._next_id = (max((t.task_id for t in self.tasks), default=0) + 1)

    # ---------- Core operations ----------

    def add_task(self, description):
        """Create a new task with the given description and persist it."""
        description = description.strip()
        if not description:
            raise ValueError("Task description cannot be empty.")

        task = Task(description=description, task_id=self._next_id)
        self.tasks.append(task)
        self._next_id += 1
        self._save()
        return task

    def remove_task(self, task_id):
        """Remove a task by ID. Raises LookupError if not found."""
        task = self._find_task(task_id)
        self.tasks.remove(task)
        self._save()
        return task

    def complete_task(self, task_id):
        """Mark a task as completed by ID. Raises LookupError if not found."""
        task = self._find_task(task_id)
        task.mark_completed()
        self._save()
        return task

    def uncomplete_task(self, task_id):
        """Mark a task as not completed (undo) by ID."""
        task = self._find_task(task_id)
        task.mark_incomplete()
        self._save()
        return task

    def list_tasks(self, filter_status="all"):
        """
        Return tasks matching a filter.

        filter_status: "all" | "pending" | "completed"
        """
        if filter_status == "pending":
            return [t for t in self.tasks if not t.completed]
        elif filter_status == "completed":
            return [t for t in self.tasks if t.completed]
        return list(self.tasks)

    # ---------- Helpers ----------

    def _find_task(self, task_id):
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        raise LookupError(f"No task found with ID {task_id}.")

    def _save(self):
        self.storage.save(self.tasks)
