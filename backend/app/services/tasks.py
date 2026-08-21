import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

TASKS_DIR = Path("tasks_data")
TASKS_DIR.mkdir(exist_ok=True)
TASKS_FILE = TASKS_DIR / "tasks.json"


def _load_tasks() -> Dict[str, Dict[str, Any]]:
    if TASKS_FILE.exists():
        try:
            return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_tasks(tasks: Dict[str, Dict[str, Any]]):
    try:
        TASKS_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    except Exception:
        pass


class TaskTracker:
    """Tracks background analysis tasks with progress (persisted to disk)."""

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = _load_tasks()

    def _persist(self):
        _save_tasks(self._tasks)

    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "message": "Task created",
            "result": None,
            "error": None,
        }
        self._persist()
        return task_id

    def update_progress(self, task_id: str, progress: int, message: str):
        if task_id in self._tasks:
            self._tasks[task_id]["progress"] = progress
            self._tasks[task_id]["message"] = message
            self._persist()

    def complete(self, task_id: str, result: Dict[str, Any]):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "completed"
            self._tasks[task_id]["progress"] = 100
            self._tasks[task_id]["message"] = "Analysis complete"
            self._tasks[task_id]["result"] = result
            self._persist()

    def fail(self, task_id: str, error: str):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "failed"
            self._tasks[task_id]["message"] = error
            self._tasks[task_id]["error"] = error
            self._persist()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)

    def start(self, task_id: str):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "processing"

    def cleanup_old_tasks(self, max_age_seconds: int = 3600):
        if len(self._tasks) > 100:
            keys = list(self._tasks.keys())
            for k in keys[:-50]:
                del self._tasks[k]


# Global task tracker instance
task_tracker = TaskTracker()
