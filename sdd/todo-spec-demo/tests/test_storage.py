import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from todo_cli.model import Task, TaskList
from todo_cli.storage import TaskStorageError, load_tasks, save_tasks


class TaskStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.path = Path(self.temporary_directory.name) / "tasks.json"

    def test_missing_and_zero_byte_files_load_as_empty(self) -> None:
        self.assertEqual(load_tasks(self.path), TaskList())
        self.path.write_bytes(b"")
        self.assertEqual(load_tasks(self.path), TaskList())

    def test_valid_document_round_trips(self) -> None:
        expected = TaskList(next_id=3, tasks=[Task(1, "Buy milk"), Task(2, "Call Sam", True)])

        save_tasks(self.path, expected)

        self.assertEqual(load_tasks(self.path).to_document(), expected.to_document())

    def test_malformed_and_unsupported_documents_are_rejected(self) -> None:
        self.path.write_text("{invalid", encoding="utf-8")
        with self.assertRaisesRegex(TaskStorageError, "not valid JSON"):
            load_tasks(self.path)

        self.path.write_text(
            json.dumps({"schema_version": 2, "next_id": 1, "tasks": []}),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(TaskStorageError, "Unsupported"):
            load_tasks(self.path)

    def test_failed_replace_preserves_previous_file_and_cleans_temporary_file(self) -> None:
        original = TaskList(next_id=2, tasks=[Task(1, "Keep me")])
        save_tasks(self.path, original)
        original_contents = self.path.read_text(encoding="utf-8")

        with patch("todo_cli.storage.os.replace", side_effect=OSError("simulated failure")):
            with self.assertRaisesRegex(TaskStorageError, "Could not save"):
                save_tasks(self.path, TaskList(next_id=3, tasks=[Task(1, "Changed")]))

        self.assertEqual(self.path.read_text(encoding="utf-8"), original_contents)
        self.assertEqual(list(self.path.parent.glob(".tasks.json.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()