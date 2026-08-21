import asyncio
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from app.models.schemas import GitHubAnalyzeRequest, TaskResult
from app.services.analysis_service import AnalysisService
from app.services.tasks import task_tracker
from app.services.pricing import check_scan_allowed, increment_scan_count
from app.utils.cache import get_url_hash, get_cached_result, set_cached_result

router = APIRouter()

TEMP_DIR = Path("temp_analysis")
TEMP_DIR.mkdir(exist_ok=True)


async def run_github_analysis(task_id: str, repo_url: str, extract_path: str):
    """Clone a GitHub repo and analyze it."""
    service = AnalysisService()
    try:
        task_tracker.start(task_id)
        task_tracker.update_progress(task_id, 10, "Cloning repository...")

        # Clone using git
        import subprocess
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", repo_url, extract_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise Exception(f"Git clone failed: {stderr.decode()[:500]}")

        task_tracker.update_progress(task_id, 40, "Repository cloned. Analyzing...")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, service.analyze, extract_path
        )

        # Cache result
        cache_key = get_url_hash(repo_url)
        set_cached_result(cache_key, result)

        task_tracker.complete(task_id, result)
    except Exception as e:
        task_tracker.fail(task_id, str(e))
    finally:
        try:
            shutil.rmtree(extract_path, ignore_errors=True)
        except Exception:
            pass


@router.post("/", response_model=TaskResult)
async def analyze_github(request: GitHubAnalyzeRequest, background_tasks: BackgroundTasks, http_request: Request):
    repo_url = request.repo_url.strip()

    if not repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Only GitHub URLs are supported (https://github.com/...).")

    # Check pricing
    access = check_scan_allowed(http_request)
    if not access["allowed"]:
        raise HTTPException(status_code=402, detail=f"Free scan limit reached ({access['remaining']} remaining). Please upgrade at /pricing.")
    increment_scan_count(http_request)

    # Check cache
    cache_key = get_url_hash(repo_url)
    cached = get_cached_result(cache_key)
    if cached:
        return {
            "task_id": cache_key,
            "status": "completed",
            "progress": 100,
            "result": cached,
        }

    repo_name = request.repo_name or repo_url.rstrip("/").split("/")[-1]
    extract_path = str(TEMP_DIR / repo_name)

    task_id = task_tracker.create_task()
    background_tasks.add_task(
        run_github_analysis, task_id, repo_url, extract_path
    )

    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 5,
        "result": None,
    }
