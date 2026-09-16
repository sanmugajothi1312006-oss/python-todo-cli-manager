"""
test_task_manager.py
---------------------
Simple automated tests for TaskManager using Python's built-in unittest
module (no external dependencies required).

Run with:
    python -m unittest tests/test_task_manager.py -v

These use a temporary file for storage so they never touch the user's real
tasks.json, and clean up after themselves.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from storage import Storage
from task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        # Use a fresh temp file for each test so tests don't interfere.
        fd, self.tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.tmp_path)  # start with no file, simulating first run
        self.manager = TaskManager(Storage(filepath=self.tmp_path))

    def tearDown(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)
        tmp = self.tmp_path + ".tmp"
        if os.path.exists(tmp):
            os.remove(tmp)

    def test_add_task(self):
        task = self.manager.add_task("Buy milk")
        self.assertEqual(task.description, "Buy milk")
        self.assertFalse(task.completed)
        self.assertEqual(len(self.manager.list_tasks()), 1)

    def test_add_empty_task_raises(self):
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    def test_complete_task(self):
        task = self.manager.add_task("Read a book")
        self.manager.complete_task(task.task_id)
        self.assertTrue(self.manager.list_tasks("completed")[0].completed)

    def test_complete_nonexistent_task_raises(self):
        with self.assertRaises(LookupError):
            self.manager.complete_task(999)

    def test_remove_task(self):
        task = self.manager.add_task("Temp task")
        self.manager.remove_task(task.task_id)
        self.assertEqual(len(self.manager.list_tasks()), 0)

    def test_remove_nonexistent_task_raises(self):
        with self.assertRaises(LookupError):
            self.manager.remove_task(42)

    def test_filter_pending_and_completed(self):
        t1 = self.manager.add_task("Task 1")
        t2 = self.manager.add_task("Task 2")
        self.manager.complete_task(t1.task_id)

        pending = self.manager.list_tasks("pending")
        completed = self.manager.list_tasks("completed")

        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].task_id, t2.task_id)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].task_id, t1.task_id)

    def test_persistence_across_manager_instances(self):
        self.manager.add_task("Persisted task")
        # Simulate restarting the app by creating a new manager on the same file
        new_manager = TaskManager(Storage(filepath=self.tmp_path))
        self.assertEqual(len(new_manager.list_tasks()), 1)
        self.assertEqual(new_manager.list_tasks()[0].description, "Persisted task")

    def test_ids_increment_and_do_not_repeat_after_removal(self):
        t1 = self.manager.add_task("A")
        self.manager.remove_task(t1.task_id)
        t2 = self.manager.add_task("B")
        self.assertNotEqual(t1.task_id, t2.task_id)


if __name__ == "__main__":
    unittest.main()
