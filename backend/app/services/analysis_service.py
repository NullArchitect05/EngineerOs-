from pathlib import Path

from app.engine.scanner import ProjectScanner
from app.engine.metrics import MetricsEngine
from app.engine.smells import SmellDetector
from app.engine.architecture import ArchitectureAnalyzer
from app.engine.report import ReportGenerator


class AnalysisService:

    def analyze(self, project_path: str):
        scanner = ProjectScanner(project_path)
        project = scanner.scan()

        metrics_engine = MetricsEngine(project_path)
        metrics = metrics_engine.compute()

        smell_detector = SmellDetector(project_path)
        smells = smell_detector.detect(metrics)

        arch_analyzer = ArchitectureAnalyzer(project_path)
        architecture = arch_analyzer.analyze()

        report_gen = ReportGenerator()
        report = report_gen.generate(project, metrics, smells, architecture)

        return {
            "status": "completed",
            "health_score": report["health_score"],
            "grade": report["grade"],
            "project": project,
            "metrics": metrics,
            "smells": smells,
            "architecture": architecture,
            "summary": {
                "repository_type": project["repository_type"],
                "primary_language": project["primary_language"],
                "health": report["health_score"],
                "grade": report["grade"],
                "strengths": report["strengths"],
                "risks": report["risks"],
                "recommendations": report["recommendations"],
                "executive_summary": report["executive_summary"],
            },
        }
