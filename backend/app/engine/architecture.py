from pathlib import Path
from typing import Dict, Any, List


class ArchitectureAnalyzer:
    """Analyzes the architectural structure of a repository."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.top_dirs = []
        self._scan_top_dirs()

    def _scan_top_dirs(self):
        try:
            self.top_dirs = [
                d.name for d in self.project_path.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
        except Exception:
            self.top_dirs = []

    def detect_pattern(self) -> str:
        dirs = set(d.lower() for d in self.top_dirs)

        # Monorepo
        if "packages" in dirs or "apps" in dirs:
            return "monorepo"

        # MVC
        if {"models", "views", "controllers"}.issubset(dirs):
            return "mvc"
        if {"models", "views", "controllers"}.issubset(set(d.lower().replace("s", "") for d in dirs)):
            return "mvc"

        # Layered
        if {"api", "services", "data", "repositories"}.intersection(dirs):
            if len({"api", "services", "data"}.intersection(dirs)) >= 2:
                return "layered"

        # Modular
        if {"src", "lib", "tests", "test"}.intersection(dirs):
            return "modular"

        # Frontend
        if {"components", "pages", "hooks"}.intersection(dirs):
            return "component_based"

        # Flat
        return "flat"

    def detect_architecture_type(self) -> str:
        pattern = self.detect_pattern()
        mapping = {
            "monorepo": "Monorepo",
            "mvc": "MVC (Model-View-Controller)",
            "layered": "Layered Architecture",
            "modular": "Modular Structure",
            "component_based": "Component-Based",
            "flat": "Flat / Unstructured",
        }
        return mapping.get(pattern, "Unknown")

    def get_top_level_structure(self) -> List[Dict[str, Any]]:
        items = []
        try:
            for item in sorted(self.project_path.iterdir()):
                name = item.name
                if name.startswith("."):
                    continue
                if item.is_dir():
                    file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                    items.append({
                        "name": name,
                        "type": "directory",
                        "file_count": file_count
                    })
                elif item.is_file():
                    items.append({
                        "name": name,
                        "type": "file",
                        "size_bytes": item.stat().st_size
                    })
        except Exception:
            pass
        return items

    def get_directory_tree(self, max_depth: int = 3) -> List[Dict[str, Any]]:
        def _build_tree(path: Path, depth: int = 0):
            if depth > max_depth:
                return None
            items = []
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith("."):
                        continue
                    if item.is_dir():
                        children = _build_tree(item, depth + 1)
                        items.append({
                            "name": item.name,
                            "type": "directory",
                            "children": children or [],
                        })
                    else:
                        items.append({
                            "name": item.name,
                            "type": "file",
                        })
            except PermissionError:
                pass
            return items

        return _build_tree(self.project_path) or []

    def analyze(self) -> Dict[str, Any]:
        pattern = self.detect_pattern()
        top_structure = self.get_top_level_structure()

        # Count directories at each level
        dir_count = 0
        file_count = 0
        for item in self.project_path.rglob("*"):
            if item.is_dir() and not any(p.startswith(".") for p in item.parts):
                dir_count += 1
            elif item.is_file():
                file_count += 1

        return {
            "top_level_directories": self.top_dirs,
            "top_level_structure": top_structure,
            "total_directories": dir_count,
            "total_files": file_count,
            "architecture_pattern": pattern,
            "architecture_type": self.detect_architecture_type(),
            "has_src_directory": "src" in [d.lower() for d in self.top_dirs],
            "has_tests_directory": any("test" in d.lower() for d in self.top_dirs),
            "is_monorepo": pattern == "monorepo",
        }

