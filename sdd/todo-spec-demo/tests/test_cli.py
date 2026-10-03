import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"


class TodoCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.working_directory = Path(self.temporary_directory.name)
        self.task_file = self.working_directory / "tasks.json"

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SOURCE_ROOT)
        return subprocess.run(
            [sys.executable, "-m", "todo_cli", *arguments],
            cwd=self.working_directory,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_add_trims_description_and_persists_pending_task_between_processes(self) -> None:
        first_result = self.run_cli("add", "  Call Sam  ")

        self.assertEqual(first_result.returncode, 0, first_result.stderr)
        self.assertIn("1", first_result.stdout)
        self.assertIn("Call Sam", first_result.stdout)
        self.assertIn("pending", first_result.stdout.lower())

        saved_document = json.loads(self.task_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_document["tasks"], [{"id": 1, "description": "Call Sam", "done": False}])
        self.assertEqual(saved_document["next_id"], 2)

        second_result = self.run_cli("add", "Buy milk")
        self.assertEqual(second_result.returncode, 0, second_result.stderr)
        self.assertIn("2", second_result.stdout)
        saved_tasks = json.loads(self.task_file.read_text(encoding="utf-8"))["tasks"]
        self.assertEqual(len(saved_tasks), 2)
        self.assertEqual(saved_tasks[0], {"id": 1, "description": "Call Sam", "done": False})

    def test_whitespace_only_description_is_rejected_without_changing_data(self) -> None:
        self.assertEqual(self.run_cli("add", "Keep this task").returncode, 0)
        original_contents = self.task_file.read_bytes()

        result = self.run_cli("add", "   ")

        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.strip())
        self.assertEqual(self.task_file.read_bytes(), original_contents)

    def test_list_shows_each_saved_task_once_with_number_and_status(self) -> None:
        self.task_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "next_id": 3,
                    "tasks": [
                        {"id": 1, "description": "Buy milk", "done": False},
                        {"id": 2, "description": "Call Sam", "done": True},
                    ],
                }
            ),
            encoding="utf-8",
        )

        result = self.run_cli("list")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("Buy milk"), 1)
        self.assertEqual(result.stdout.count("Call Sam"), 1)
        self.assertIn("1", result.stdout)
        self.assertIn("2", result.stdout)
        self.assertIn("pending", result.stdout.lower())
        self.assertIn("done", result.stdout.lower())

    def test_list_reports_empty_for_missing_and_zero_byte_files(self) -> None:
        missing_result = self.run_cli("list")
        self.assertEqual(missing_result.returncode, 0, missing_result.stderr)
        self.assertIn("No tasks", missing_result.stdout)

        self.task_file.write_bytes(b"")
        empty_result = self.run_cli("list")
        self.assertEqual(empty_result.returncode, 0, empty_result.stderr)
        self.assertIn("No tasks", empty_result.stdout)
        self.assertNotIn("pending", empty_result.stdout.lower())
        self.assertNotIn("done", empty_result.stdout.lower())

    def test_list_handles_one_thousand_tasks_without_losing_identity_or_status(self) -> None:
        tasks = [
            {"id": task_id, "description": f"Task {task_id}", "done": task_id % 2 == 0}
            for task_id in range(1, 1001)
        ]
        self.task_file.write_text(
            json.dumps({"schema_version": 1, "next_id": 1001, "tasks": tasks}),
            encoding="utf-8",
        )

        result = self.run_cli("list")

        self.assertEqual(result.returncode, 0, result.stderr)
        output_lines = result.stdout.splitlines()
        self.assertEqual(len(output_lines), 1000)
        self.assertEqual(output_lines[0], "1. [pending] Task 1")
        self.assertEqual(output_lines[-1], "1000. [done] Task 1000")

    def test_complete_is_idempotent_and_delete_preserves_other_task_ids(self) -> None:
        self.task_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "next_id": 3,
                    "tasks": [
                        {"id": 1, "description": "Finish report", "done": False},
                        {"id": 2, "description": "Send invoice", "done": False},
                    ],
                }
            ),
            encoding="utf-8",
        )

        completed_result = self.run_cli("complete", "1")
        self.assertEqual(completed_result.returncode, 0, completed_result.stderr)
        self.assertIn("1", completed_result.stdout)
        self.assertIn("done", completed_result.stdout.lower())

        repeated_result = self.run_cli("complete", "1")
        self.assertEqual(repeated_result.returncode, 0, repeated_result.stderr)
        after_repeat = json.loads(self.task_file.read_text(encoding="utf-8"))
        self.assertEqual(len(after_repeat["tasks"]), 2)
        self.assertTrue(after_repeat["tasks"][0]["done"])
        self.assertEqual(after_repeat["tasks"][0]["description"], "Finish report")

        deleted_result = self.run_cli("delete", "2")
        self.assertEqual(deleted_result.returncode, 0, deleted_result.stderr)
        after_delete = json.loads(self.task_file.read_text(encoding="utf-8"))
        self.assertEqual(after_delete["tasks"], [{"id": 1, "description": "Finish report", "done": True}])

        listed_result = self.run_cli("list")
        self.assertEqual(listed_result.returncode, 0, listed_result.stderr)
        self.assertIn("1", listed_result.stdout)
        self.assertIn("done", listed_result.stdout.lower())
        self.assertNotIn("Send invoice", listed_result.stdout)

        self.assertEqual(self.run_cli("delete", "1").returncode, 0)
        empty_result = self.run_cli("list")
        self.assertEqual(empty_result.returncode, 0, empty_result.stderr)
        self.assertEqual(empty_result.stdout.strip(), "No tasks.")
        next_result = self.run_cli("add", "New task")
        self.assertEqual(next_result.returncode, 0, next_result.stderr)
        self.assertIn("3", next_result.stdout)

    def test_invalid_and_unknown_task_numbers_do_not_change_saved_data(self) -> None:
        self.task_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "next_id": 2,
                    "tasks": [{"id": 1, "description": "Keep task", "done": False}],
                }
            ),
            encoding="utf-8",
        )
        original_contents = self.task_file.read_bytes()

        for arguments, expected_status in (
            (("complete", "abc"), 2),
            (("complete", "-1"), 2),
            (("delete", "0"), 2),
            (("complete", "999"), 1),
            (("delete", "999"), 1),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, expected_status, result.stderr)
                self.assertTrue(result.stderr.strip())
                self.assertEqual(self.task_file.read_bytes(), original_contents)


if __name__ == "__main__":
    unittest.main()