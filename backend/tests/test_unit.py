"""Unit tests for EngineerOS backend services."""
import os
import sys
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.tasks import TaskTracker
from app.services.pricing import get_free_scan_limit, get_monthly_price
from app.engine.report import ReportGenerator


class TestTaskTracker:
    def setup_method(self):
        self.tracker = TaskTracker()
        self.tracker._tasks = {}

    def test_create_task(self):
        task_id = self.tracker.create_task()
        assert task_id is not None
        task = self.tracker.get_task(task_id)
        assert task["status"] == "pending"

    def test_update_progress(self):
        task_id = self.tracker.create_task()
        self.tracker.start(task_id)
        self.tracker.update_progress(task_id, 50, "Processing")
        task = self.tracker.get_task(task_id)
        assert task["progress"] == 50

    def test_complete_task(self):
        task_id = self.tracker.create_task()
        self.tracker.complete(task_id, {"score": 85})
        task = self.tracker.get_task(task_id)
        assert task["status"] == "completed"
        assert task["result"]["score"] == 85

    def test_fail_task(self):
        task_id = self.tracker.create_task()
        self.tracker.fail(task_id, "error")
        task = self.tracker.get_task(task_id)
        assert task["status"] == "failed"

    def test_nonexistent_task(self):
        assert self.tracker.get_task("bad") is None

    def test_cleanup(self):
        for _ in range(120):
            self.tracker.create_task()
        self.tracker.cleanup_old_tasks()
        assert len(self.tracker._tasks) <= 50


class TestPricing:
    def test_free_scan_limit(self):
        assert get_free_scan_limit() == 3

    def test_monthly_price(self):
        assert get_monthly_price() == 5.99

    def test_check_scan_allowed(self):
        mock_req = Mock()
        mock_req.client.host = "127.0.0.1"
        mock_req.headers = {}
        from app.services.pricing import check_scan_allowed, increment_scan_count
        result = check_scan_allowed(mock_req)
        assert result["allowed"] is True
        assert result["remaining"] == 3

    def test_increment_scan_count(self):
        mock_req = Mock()
        mock_req.client.host = "9.9.9.9"  # Unique IP to avoid conflicts
        mock_req.headers = {}
        from app.services.pricing import increment_scan_count, check_scan_allowed
        result = check_scan_allowed(mock_req)
        assert result["remaining"] >= 0
        increment_scan_count(mock_req)
        result = check_scan_allowed(mock_req)
        assert result["remaining"] == 2


class TestReportGenerator:
    def setup_method(self):
        self.gen = ReportGenerator()

    def test_grade(self):
        assert self.gen.get_grade(95) == "A"
        assert self.gen.get_grade(82) == "B"
        assert self.gen.get_grade(70) == "C"
        assert self.gen.get_grade(55) == "D"
        assert self.gen.get_grade(30) == "F"

    def test_health_score_bounds(self):
        score = self.gen.calculate_health_score(
            strengths=[], risks=[],
            metrics={"total_complexity": 0, "total_files": 10, "code_files_scanned": 1},
            smells_count=0,
            architecture={"architecture_type": "Modular", "has_src_directory": True, "has_tests_directory": True}
        )
        assert 0 <= score <= 100

    def test_executive_summary(self):
        s = self.gen.generate_executive_summary(
            {"project_name": "myrepo", "primary_language": "Python", "repository_type": "API"}, 80, "Modular"
        )
        assert "myrepo" in s
        assert "Python" in s

    def test_generate_report_has_all_keys(self):
        r = self.gen.generate(
            project_info={"project_name": "t", "has_readme": True, "has_tests": True, "primary_language": "Py", "repository_type": "App"},
            metrics={"total_code_lines": 500, "comment_ratio": 0.15, "total_complexity": 10, "code_files_scanned": 5, "total_files": 10},
            smells={"total_smells": 0, "smells": []},
            architecture={"architecture_type": "Modular", "has_src_directory": True, "has_tests_directory": True, "is_monorepo": False}
        )
        for key in ["health_score", "grade", "strengths", "risks", "recommendations", "executive_summary"]:
            assert key in r