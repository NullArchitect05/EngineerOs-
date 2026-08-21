import asyncio
import shutil
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models.schemas import CompareRequest, CompareGitHubRequest, TaskResult
from app.services.analysis_service import AnalysisService
from app.services.tasks import task_tracker
from app.utils.zip_utils import extract_zip

router = APIRouter()

TEMP_DIR = Path("temp_analysis")
TEMP_DIR.mkdir(exist_ok=True)


async def run_compare_zip_task(task_id: str, path_a: str, path_b: str):
    """Analyze two repos and compare them."""
    service = AnalysisService()
    try:
        task_tracker.start(task_id)
        task_tracker.update_progress(task_id, 20, "Analyzing Repository A...")

        loop = asyncio.get_event_loop()
        result_a = await loop.run_in_executor(None, service.analyze, path_a)

        task_tracker.update_progress(task_id, 50, "Analyzing Repository B...")
        result_b = await loop.run_in_executor(None, service.analyze, path_b)

        task_tracker.update_progress(task_id, 80, "Comparing results...")

        comparison = {
            "repo_a": result_a,
            "repo_b": result_b,
            "comparison": {
                "health_diff": result_a["health_score"] - result_b["health_score"],
                "file_count_a": result_a["project"]["total_files"],
                "file_count_b": result_b["project"]["total_files"],
                "frameworks_a": result_a["project"]["frameworks"],
                "frameworks_b": result_b["project"]["frameworks"],
                "language_a": result_a["project"]["primary_language"],
                "language_b": result_b["project"]["primary_language"],
                "winner": "repo_a" if result_a["health_score"] >= result_b["health_score"] else "repo_b",
                "winner_score": max(result_a["health_score"], result_b["health_score"]),
            }
        }

        task_tracker.complete(task_id, comparison)
    except Exception as e:
        task_tracker.fail(task_id, str(e))
    finally:
        for p in [path_a, path_b]:
            try:
                shutil.rmtree(p, ignore_errors=True)
            except Exception:
                pass


@router.post("/zip", response_model=TaskResult)
async def compare_repos(request: CompareRequest, background_tasks: BackgroundTasks):
    zip_a = Path("uploads") / f"{request.file_id_a}.zip"
    zip_b = Path("uploads") / f"{request.file_id_b}.zip"

    if not zip_a.exists() or not zip_b.exists():
        raise HTTPException(status_code=404, detail="One or both repositories not found.")

    path_a = TEMP_DIR / request.file_id_a
    path_b = TEMP_DIR / request.file_id_b

    extract_zip(str(zip_a), str(path_a))
    extract_zip(str(zip_b), str(path_b))

    task_id = task_tracker.create_task()
    background_tasks.add_task(run_compare_zip_task, task_id, str(path_a), str(path_b))

async def run_compare_github_task(task_id: str, url_a: str, url_b: str,
                                   path_a: str, path_b: str):
    """Clone two GitHub repos and compare."""
    import subprocess
    service = AnalysisService()
    try:
        task_tracker.start(task_id)
        task_tracker.update_progress(task_id, 10, "Cloning Repository A...")

        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", url_a, path_a,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        task_tracker.update_progress(task_id, 30, "Cloning Repository B...")
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", url_b, path_b,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        task_tracker.update_progress(task_id, 50, "Analyzing both...")
        loop = asyncio.get_event_loop()
        result_a, result_b = await asyncio.gather(
            loop.run_in_executor(None, service.analyze, path_a),
            loop.run_in_executor(None, service.analyze, path_b),
        )

        comparison = {
            "repo_a": result_a, "repo_b": result_b,
            "comparison": {
                "health_diff": result_a["health_score"] - result_b["health_score"],
                "file_count_a": result_a["project"]["total_files"],
                "file_count_b": result_b["project"]["total_files"],
                "frameworks_a": result_a["project"]["frameworks"],
                "frameworks_b": result_b["project"]["frameworks"],
                "winner": "repo_a" if result_a["health_score"] >= result_b["health_score"] else "repo_b",
                "winner_score": max(result_a["health_score"], result_b["health_score"]),
            }
        }
        task_tracker.complete(task_id, comparison)
    except Exception as e:
        task_tracker.fail(task_id, str(e))
    finally:
        for p in [path_a, path_b]:
            try:
                shutil.rmtree(p, ignore_errors=True)
            except Exception:
                pass


@router.post("/github", response_model=TaskResult)
async def compare_github_repos(request: CompareGitHubRequest, background_tasks: BackgroundTasks):
    url_a = request.repo_url_a.strip()
    url_b = request.repo_url_b.strip()

    for url in [url_a, url_b]:
        if not url.startswith("https://github.com/"):
            raise HTTPException(status_code=400, detail=f"Invalid GitHub URL: {url}")

    name_a = url_a.rstrip("/").split("/")[-1]
    name_b = url_b.rstrip("/").split("/")[-1]
    path_a = str(TEMP_DIR / f"compare_{name_a}")
    path_b = str(TEMP_DIR / f"compare_{name_b}")

    task_id = task_tracker.create_task()
    background_tasks.add_task(run_compare_github_task, task_id, url_a, url_b, path_a, path_b)

    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 5,
        "result": None,
    }

    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 5,
        "result": None,
    }
