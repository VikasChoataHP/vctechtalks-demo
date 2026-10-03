from dataclasses import dataclass, field
from typing import Any


class TaskDataError(ValueError):
    """Raised when persisted task data does not match the supported schema."""


@dataclass(frozen=True)
class Task:
    id: int
    description: str
    done: bool = False


@dataclass
class TaskList:
    next_id: int = 1
    tasks: list[Task] = field(default_factory=list)

    def add(self, description: str) -> Task:
        normalized_description = description.strip()
        if not normalized_description:
            raise ValueError("Task description cannot be empty.")
        if type(self.next_id) is not int or self.next_id < 1:
            raise ValueError("The next task number must be a positive integer.")

        task = Task(self.next_id, normalized_description)
        self.tasks.append(task)
        self.next_id += 1
        return task

    def complete(self, task_id: int) -> Task:
        task_index = self._task_index(task_id)
        task = self.tasks[task_index]
        if not task.done:
            task = Task(task.id, task.description, True)
            self.tasks[task_index] = task
        return task

    def delete(self, task_id: int) -> Task:
        task_index = self._task_index(task_id)
        return self.tasks.pop(task_index)

    def _task_index(self, task_id: int) -> int:
        if type(task_id) is not int or task_id < 1:
            raise ValueError("Task number must be a positive integer.")
        for index, task in enumerate(self.tasks):
            if task.id == task_id:
                return index
        raise LookupError(f"No task numbered {task_id} exists.")

    @classmethod
    def from_document(cls, document: Any) -> "TaskList":
        if not isinstance(document, dict):
            raise TaskDataError("Task data must be a JSON object.")

        if set(document) != {"schema_version", "next_id", "tasks"}:
            raise TaskDataError("Task data must contain schema_version, next_id, and tasks only.")

        schema_version = document["schema_version"]
        if type(schema_version) is not int or schema_version != 1:
            raise TaskDataError("Unsupported task data schema version.")

        next_id = document["next_id"]
        if type(next_id) is not int or next_id < 1:
            raise TaskDataError("next_id must be a positive integer.")

        records = document["tasks"]
        if not isinstance(records, list):
            raise TaskDataError("tasks must be a JSON array.")

        tasks: list[Task] = []
        seen_ids: set[int] = set()
        for index, record in enumerate(records):
            if not isinstance(record, dict) or set(record) != {"id", "description", "done"}:
                raise TaskDataError(f"Task at index {index} has invalid fields.")

            task_id = record["id"]
            description = record["description"]
            done = record["done"]
            if type(task_id) is not int or task_id < 1:
                raise TaskDataError(f"Task at index {index} must have a positive integer id.")
            if task_id in seen_ids:
                raise TaskDataError(f"Task id {task_id} is duplicated.")
            if not isinstance(description, str) or not description.strip():
                raise TaskDataError(f"Task {task_id} must have a non-empty description.")
            if type(done) is not bool:
                raise TaskDataError(f"Task {task_id} done status must be a boolean.")

            seen_ids.add(task_id)
            tasks.append(Task(task_id, description, done))

        if seen_ids and next_id <= max(seen_ids):
            raise TaskDataError("next_id must be greater than every task id.")

        return cls(next_id=next_id, tasks=tasks)

    def to_document(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "next_id": self.next_id,
            "tasks": [
                {"id": task.id, "description": task.description, "done": task.done}
                for task in self.tasks
            ],
        }