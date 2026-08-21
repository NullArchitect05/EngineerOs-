from fastapi import APIRouter, HTTPException

from app.models.schemas import TaskResult
from app.services.tasks import task_tracker

router = APIRouter()


@router.get("/{task_id}", response_model=TaskResult)
async def get_results(task_id: str):
    task = task_tracker.get_task(task_id)

    if not task:
        # Check if it's a cached file_id result
        from app.utils.cache import get_cached_result
        cached = get_cached_result(task_id)
        if cached:
            return {
                "task_id": task_id,
                "status": "completed",
                "progress": 100,
                "result": cached,
            }
        raise HTTPException(status_code=404, detail="Task not found.")

    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "message": task["message"],
        "result": task["result"],
        "error": task["error"],
    }