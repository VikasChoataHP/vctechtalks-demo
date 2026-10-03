import json
import os
import tempfile
from pathlib import Path

from .model import TaskDataError, TaskList


class TaskStorageError(Exception):
    """Raised when task data cannot be read or safely written."""


def load_tasks(path: Path) -> TaskList:
    try:
        contents = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return TaskList()
    except (OSError, UnicodeError) as error:
        raise TaskStorageError(f"Could not read task data: {error}") from error

    if not contents:
        return TaskList()

    try:
        document = json.loads(contents)
    except json.JSONDecodeError as error:
        raise TaskStorageError(f"Task data is not valid JSON: {error.msg}") from error

    try:
        return TaskList.from_document(document)
    except TaskDataError as error:
        raise TaskStorageError(f"Task data is invalid: {error}") from error


def save_tasks(path: Path, task_list: TaskList) -> None:
    try:
        document = TaskList.from_document(task_list.to_document()).to_document()
    except (AttributeError, TaskDataError) as error:
        raise TaskStorageError(f"Task data is invalid: {error}") from error

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(document, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, path)
        temporary_path = None
    except (OSError, TypeError, ValueError) as error:
        raise TaskStorageError(f"Could not save task data: {error}") from error
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                pass