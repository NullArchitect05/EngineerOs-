"""Route to trigger AI-powered analysis on completed results."""
from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import TaskResult
from app.services.tasks import task_tracker
from app.services.ai_analysis import enhance_analysis_with_ai
from app.utils.cache import get_cached_result, set_cached_result

router = APIRouter()


@router.post("/{task_id}", response_model=TaskResult)
async def ai_analyze_task(task_id: str, request: Request):
    """Take an existing analysis result and enhance it with AI insights."""
    task = task_tracker.get_task(task_id)

    if not task:
        # Try cache
        cached = get_cached_result(task_id)
        if cached:
            task = {"status": "completed", "result": cached, "progress": 100}
        else:
            raise HTTPException(status_code=404, detail="Task not found.")

    if task["status"] != "completed" or not task.get("result"):
        raise HTTPException(status_code=400, detail="Task is not yet completed.")

    result = task["result"]
    enhanced = await enhance_analysis_with_ai(result)

    # Update task with enhanced result
    if task_id in task_tracker._tasks:
        task_tracker._tasks[task_id]["result"] = enhanced
    else:
        # If it was a cached result, update cache
        set_cached_result(task_id, enhanced)

    return {
        "task_id": task_id,
        "status": "completed",
        "progress": 100,
        "result": enhanced,
    }
