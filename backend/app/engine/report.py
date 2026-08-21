from typing import Dict, Any, List


class ReportGenerator:
    """Generates structured engineering reports from analysis data."""

    def generate(self, project_info: Dict[str, Any], metrics: Dict[str, Any],
                 smells: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        strengths = []
        risks = []
        recommendations = []

        # --- Analyze metrics ---
        if metrics["total_code_lines"] > 0:
            if metrics["comment_ratio"] > 0.1:
                strengths.append(f"Good documentation ratio ({metrics['comment_ratio']:.0%} comments).")
            else:
                risks.append(f"Low documentation ratio ({metrics['comment_ratio']:.0%} comments).")
                recommendations.append("Add more comments and docstrings to improve code readability.")

        if metrics["total_complexity"] > 0:
            avg_complexity = metrics["total_complexity"] / max(metrics["code_files_scanned"], 1)
            if avg_complexity < 2:
                strengths.append(f"Low average cyclomatic complexity ({avg_complexity:.1f}) — easy to test.")
            elif avg_complexity < 4:
                strengths.append(f"Moderate complexity ({avg_complexity:.1f}) — acceptable.")
            else:
                risks.append(f"High average complexity ({avg_complexity:.1f}).")
                recommendations.append("Refactor complex functions to reduce complexity.")

        if metrics["code_files_scanned"] < 10:
            risks.append("Very small codebase — may lack substance.")
            recommendations.append("Consider expanding the project with more functionality.")

        # --- Analyze smells ---
        if smells["total_smells"] == 0:
            strengths.append("No code smells detected — codebase is clean.")
        else:
            for smell in smells["smells"]:
                risks.append(smell["message"])
                recommendations.append(smell["recommendation"])

        # --- Analyze architecture ---
        arch_type = architecture["architecture_type"]
        if architecture["has_src_directory"]:
            strengths.append("Organized structure with src/ directory.")
        if architecture["has_tests_directory"]:
            strengths.append("Dedicated tests/ directory detected.")
        if architecture["is_monorepo"]:
            strengths.append("Monorepo structure detected — good for multi-package projects.")

        if arch_type == "Flat / Unstructured":
            risks.append("No clear architectural pattern detected.")
            recommendations.append("Consider organizing files into a structured folder layout.")

        # --- Analyze project info ---
        if project_info.get("has_readme"):
            strengths.append("README documentation present.")
        else:
            risks.append("No README found.")
            recommendations.append("Add a README.md with project description, setup, and usage.")

        if project_info.get("has_tests"):
            strengths.append("Test files detected.")
        else:
            risks.append("No tests detected.")
            recommendations.append("Add automated tests to ensure code reliability.")

        # --- Build report ---
        health_score = self.calculate_health_score(
            strengths=strengths, risks=risks, metrics=metrics,
            smells_count=smells["total_smells"], architecture=architecture
        )

        return {
            "health_score": health_score,
            "strengths": strengths[:8],
            "risks": risks[:8],
            "recommendations": recommendations[:8],
            "executive_summary": self.generate_executive_summary(
                project_info, health_score, arch_type
            ),
            "grade": self.get_grade(health_score),
        }

    def calculate_health_score(self, strengths: List[str], risks: List[str],
                                metrics: Dict[str, Any], smells_count: int,
                                architecture: Dict[str, Any]) -> int:
        score = 70
        score += len(strengths) * 5
        score -= len(risks) * 8
        score -= smells_count * 5

        if metrics.get("total_complexity", 0) > 0:
            avg_complexity = metrics["total_complexity"] / max(metrics.get("code_files_scanned", 1), 1)
            if avg_complexity > 5:
                score -= 10
            elif avg_complexity > 3:
                score -= 5

        if architecture["architecture_type"] != "Flat / Unstructured":
            score += 5
        if architecture["has_src_directory"]:
            score += 5
        if architecture["has_tests_directory"]:
            score += 5

        total = metrics.get("total_files", 0)
        if 20 <= total <= 200:
            score += 5
        elif total > 500:
            score -= 5

        return max(0, min(100, score))

    def get_grade(self, score: int) -> str:
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 65:
            return "C"
        elif score >= 50:
            return "D"
        return "F"

    def generate_executive_summary(self, project_info: Dict[str, Any],
                                    score: int, arch_type: str) -> str:
        name = project_info.get("project_name", "Repository")
        lang = project_info.get("primary_language", "Unknown")
        repo_type = project_info.get("repository_type", "Software Project")
        grade = self.get_grade(score)

        return (
            f"{name} is a {repo_type} primarily written in {lang} "
            f"with a {arch_type} structure. "
            f"It has earned an engineering health score of {score}/100 "
            f"(Grade: {grade}). "
            f"{'Strong codebase with good practices in place.' if score >= 70 else 'There are areas that need attention to improve code quality and maintainability.'}"
        )

