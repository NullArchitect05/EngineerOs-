"""Integration tests for EngineerOS API and full analysis pipeline."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestFullAnalysis:
    """Test the full analysis pipeline with a temp project."""

    def test_scan_project(self, tmp_path):
        from app.engine.scanner import ProjectScanner
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "__init__.py").write_text("")
        (tmp_path / "src" / "main.py").write_text('"""Module."""\n\ndef hello():\n    x = 1\n    if x:\n        print(x)\n    return x\n')
        (tmp_path / "README.md").write_text("# Test\n")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_main.py").write_text("def test_x(): assert True\n")

        scanner = ProjectScanner(str(tmp_path))
        project = scanner.scan()
        assert project["total_files"] >= 3
        assert project["primary_language"] == "Python"
        assert project["has_readme"] is True
        assert project["has_tests"] is True

    def test_metrics_compute(self, tmp_path):
        from app.engine.metrics import MetricsEngine
        (tmp_path / "code.py").write_text("# comment\nx=1\ny=2\n")
        metrics = MetricsEngine(str(tmp_path)).compute()
        assert metrics["total_code_lines"] > 0
        assert metrics["comment_ratio"] >= 0

    def test_architecture_detection(self, tmp_path):
        from app.engine.architecture import ArchitectureAnalyzer
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("")
        arch = ArchitectureAnalyzer(str(tmp_path)).analyze()
        assert arch["has_src_directory"] is True
        assert "architecture_type" in arch

    def test_smell_detection(self, tmp_path):
        from app.engine.metrics import MetricsEngine
        from app.engine.smells import SmellDetector
        (tmp_path / "large.py").write_text("\n".join([f"line_{i}" for i in range(1000)]))
        metrics = MetricsEngine(str(tmp_path)).compute()
        smells = SmellDetector(str(tmp_path)).detect(metrics)
        assert "total_smells" in smells

    def test_full_pipeline(self, tmp_path):
        from app.engine.scanner import ProjectScanner
        from app.engine.metrics import MetricsEngine
        from app.engine.smells import SmellDetector
        from app.engine.architecture import ArchitectureAnalyzer
        from app.engine.report import ReportGenerator

        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text('"""App."""\ndef run():\n    pass\n')
        (tmp_path / "README.md").write_text("# Project\n")

        project = ProjectScanner(str(tmp_path)).scan()
        metrics = MetricsEngine(str(tmp_path)).compute()
        smells = SmellDetector(str(tmp_path)).detect(metrics)
        arch = ArchitectureAnalyzer(str(tmp_path)).analyze()
        report = ReportGenerator().generate(project, metrics, smells, arch)

        assert 0 <= report["health_score"] <= 100
        assert report["grade"] in ["A", "B", "C", "D", "F"]
        assert len(report["strengths"]) >= 0


class TestAPIEndpoints:
    """Test FastAPI endpoints."""

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_pricing_status(self, client):
        resp = client.get("/pricing/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "free_limit" in data
        assert "monthly_price" in data

    def test_pricing_check(self, client):
        resp = client.get("/pricing/check")
        assert resp.status_code == 200

    def test_upload_no_file_validation(self, client):
        resp = client.post("/upload/")
        assert resp.status_code == 422

    def test_github_no_url_validation(self, client):
        resp = client.post("/analyze/github/", json={})
        assert resp.status_code == 422

    def test_bad_task_result(self, client):
        resp = client.get("/results/nonexistent")
        assert resp.status_code == 404