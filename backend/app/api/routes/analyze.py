from pathlib import Path
import asyncio
import shutil

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from app.models.schemas import AnalyzeRequest, TaskResult
from app.services.analysis_service import AnalysisService
from app.services.tasks import task_tracker
from app.services.pricing import check_scan_allowed, increment_scan_count
from app.utils.zip_utils import extract_zip
from app.utils.cache import get_file_hash, get_cached_result, set_cached_result

router = APIRouter()

UPLOAD_DIR = Path("uploads")
TEMP_DIR = Path("temp_analysis")
TEMP_DIR.mkdir(exist_ok=True)


async def run_analysis_task(task_id: str, project_folder: str, cache_key: str = None):
    """Background task that runs analysis with progress updates."""
    service = AnalysisService()
    try:
        task_tracker.start(task_id)
        task_tracker.update_progress(task_id, 10, "Extracting repository...")

        # Check cache
        if cache_key:
            cached = get_cached_result(cache_key)
            if cached:
                task_tracker.update_progress(task_id, 50, "Loading from cache...")
                await asyncio.sleep(0.2)
                task_tracker.complete(task_id, cached)
                return

        task_tracker.update_progress(task_id, 30, "Scanning project structure...")

        # Run analysis (blocking CPU work in executor)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, service.analyze, str(project_folder)
        )

        task_tracker.update_progress(task_id, 85, "Generating report...")
        await asyncio.sleep(0.3)
        result["cached"] = False

        if cache_key:
            set_cached_result(cache_key, result)
            result["cached"] = True

        task_tracker.complete(task_id, result)
    except Exception as e:
        task_tracker.fail(task_id, str(e))
    finally:
        # Cleanup temp folder
        try:
            if project_folder.startswith(str(TEMP_DIR)):
                shutil.rmtree(project_folder, ignore_errors=True)
        except Exception:
            pass


@router.post("/", response_model=TaskResult)
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks, http_request: Request):
    zip_path = UPLOAD_DIR / f"{request.file_id}.zip"

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Uploaded repository not found.")

    # Check pricing (free tier limit)
    access = check_scan_allowed(http_request)
    if not access["allowed"]:
        raise HTTPException(
            status_code=402,
            detail=f"Free scan limit reached ({access['remaining']} remaining). Please upgrade at /pricing."
        )

    # Increment scan count
    increment_scan_count(http_request)

    file_hash = get_file_hash(str(zip_path))

    # Check cache before even extracting
    cached = get_cached_result(file_hash)
    if cached:
        task_id = task_tracker.create_task()
        task_tracker.start(task_id)
        task_tracker.update_progress(task_id, 100, "Loaded from cache")
        task_tracker.complete(task_id, cached)
        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "result": cached,
        }

    project_folder = UPLOAD_DIR / request.file_id
    extract_zip(str(zip_path), str(project_folder))

    task_id = task_tracker.create_task()
    background_tasks.add_task(
        run_analysis_task, task_id, str(project_folder), file_hash
    )

    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 5,
        "result": None,
    }
