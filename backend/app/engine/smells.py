from pathlib import Path
from typing import List, Dict, Any


class SmellDetector:
    """Detects code smells and anti-patterns in a repository."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def detect(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        smells = []
        risks = []

        # Large files
        large_threshold = 500
        large_files = []
        for item in self.project_path.rglob("*"):
            if item.is_file():
                try:
                    lines = len(open(item, "r", encoding="utf-8", errors="ignore").read().splitlines())
                    if lines > large_threshold:
                        rel = item.relative_to(self.project_path)
                        large_files.append({"file": str(rel), "lines": lines})
                except Exception:
                    pass

        if large_files:
            smells.append({
                "type": "large_files",
                "severity": "medium",
                "message": f"Found {len(large_files)} files exceeding {large_threshold} lines",
                "items": sorted(large_files, key=lambda x: x["lines"], reverse=True)[:10],
                "recommendation": "Consider breaking large files into smaller modules for better maintainability."
            })

        # Mixed languages in directory
        ext_by_dir = {}
        for item in self.project_path.rglob("*"):
            if item.is_file() and item.suffix:
                parent = str(item.parent)
                if parent not in ext_by_dir:
                    ext_by_dir[parent] = set()
                ext_by_dir[parent].add(item.suffix.lower())

        mixed_dirs = []
        for dir_path, exts in ext_by_dir.items():
            code_exts = {e for e in exts if e in {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".php", ".cpp", ".c"}}
            if len(code_exts) > 1:
                try:
                    rel = Path(dir_path).relative_to(self.project_path)
                    mixed_dirs.append(str(rel))
                except ValueError:
                    pass

        if mixed_dirs:
            smells.append({
                "type": "mixed_languages",
                "severity": "low",
                "message": f"Found {len(mixed_dirs)} directories with mixed programming languages",
                "items": mixed_dirs[:10],
                "recommendation": "Consider separating different languages into dedicated directories."
            })

        # Deeply nested directories
        deep_dirs = []
        for item in self.project_path.rglob("*"):
            if item.is_dir():
                try:
                    depth = len(item.relative_to(self.project_path).parts)
                    if depth > 5:
                        deep_dirs.append(str(item.relative_to(self.project_path)))
                except ValueError:
                    pass

        if deep_dirs:
            smells.append({
                "type": "deep_nesting",
                "severity": "medium",
                "message": f"Found {len(deep_dirs)} directories with depth > 5",
                "items": deep_dirs[:10],
                "recommendation": "Consider flattening deeply nested directories to improve navigability."
            })

        # Missing __init__.py in Python packages
        python_dirs = []
        for item in self.project_path.rglob("*.py"):
            dir_ = item.parent
            if dir_ not in python_dirs and dir_ != self.project_path:
                python_dirs.append(dir_)

        missing_init = []
        for d in python_dirs:
            init_file = d / "__init__.py"
            if not init_file.exists():
                try:
                    missing_init.append(str(d.relative_to(self.project_path)))
                except ValueError:
                    pass

        if missing_init:
            smells.append({
                "type": "missing_init",
                "severity": "low",
                "message": f"Found {len(missing_init)} Python directories without __init__.py",
                "items": missing_init[:10],
                "recommendation": "Add __init__.py files to Python directories to make them proper packages."
            })

        # No .gitignore
        gitignore = self.project_path / ".gitignore"
        if not gitignore.exists():
            risks.append("No .gitignore file found. Version control hygiene could be improved.")

        return {
            "smells": smells,
            "total_smells": len(smells),
            "risks": risks,
            "overall_assessment": "good" if len(smells) <= 2 else "fair" if len(smells) <= 5 else "needs_improvement"
        }

