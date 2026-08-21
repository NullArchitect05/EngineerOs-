from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class AnalyzeRequest(BaseModel):
    file_id: str


class GitHubAnalyzeRequest(BaseModel):
    repo_url: str
    repo_name: Optional[str] = None


class CompareRequest(BaseModel):
    file_id_a: str
    file_id_b: str


class CompareGitHubRequest(BaseModel):
    repo_url_a: str
    repo_url_b: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    message: Optional[str] = None


class TaskResult(BaseModel):
    task_id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ScanResponse(BaseModel):
    status: str
    project: dict
