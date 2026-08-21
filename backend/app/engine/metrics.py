from pathlib import Path
from typing import Dict, Any
import ast

from app.utils.ast_utils import parse_python_file


SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".webp",
    ".tiff", ".tif", ".avif",
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
    ".mp3", ".wav", ".ogg", ".flac", ".aac",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".out", ".o", ".obj",
    ".lib", ".a", ".class", ".pyc", ".pyo",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".lock", ".map", ".swp", ".swo",
}

MAX_FILE_SIZE = 1_000_000


class MetricsEngine:
    """Computes code quality metrics from a scanned repository."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def should_skip_file(self, path: Path) -> bool:
        ext = path.suffix.lower()
        if ext in SKIP_EXTENSIONS:
            return True
        if not ext:
            return True
        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                return True
        except OSError:
            return True
        return False

    def get_code_files(self):
        files = []
        for item in self.project_path.rglob("*"):
            if item.is_file() and not self.should_skip_file(item):
                files.append(item)
        return files

    def count_lines(self, file_path: Path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.splitlines()
                total = len(lines)
                code = 0
                comments = 0
                blanks = 0
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        blanks += 1
                    elif stripped.startswith("#") or stripped.startswith("//"):
                        comments += 1
                    elif stripped.startswith("/*") or stripped.startswith("*"):
                        comments += 1
                    elif stripped.startswith("--"):
                        comments += 1
                    else:
                        code += 1
                return {"total": total, "code": code, "comments": comments, "blanks": blanks}
        except Exception:
            return {"total": 0, "code": 0, "comments": 0, "blanks": 0}

    def compute_complexity(self, file_path: Path):
        if file_path.suffix != ".py":
            return 0
        try:
            tree = parse_python_file(str(file_path))
            complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
                elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                    complexity += 1
            return complexity
        except Exception:
            return 0

    def compute(self) -> Dict[str, Any]:
        code_files = self.get_code_files()
        total_lines = 0
        total_code_lines = 0
        total_comment_lines = 0
        total_blank_lines = 0
        total_complexity = 0
        extension_counts = {}
        file_sizes = []

        for file in code_files:
            lc = self.count_lines(file)
            total_lines += lc["total"]
            total_code_lines += lc["code"]
            total_comment_lines += lc["comments"]
            total_blank_lines += lc["blanks"]
            total_complexity += self.compute_complexity(file)
            ext = file.suffix.lower()
            extension_counts[ext] = extension_counts.get(ext, 0) + 1
            try:
                file_sizes.append(file.stat().st_size)
            except OSError:
                pass

        depths = []
        for item in self.project_path.rglob("*"):
            if item.is_dir():
                try:
                    rel = item.relative_to(self.project_path)
                    depths.append(len(rel.parts))
                except ValueError:
                    depths.append(0)

        avg_file_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
        max_depth = max(depths) if depths else 0

        return {
            "total_files": len(code_files),
            "total_lines": total_lines,
            "total_code_lines": total_code_lines,
            "total_comment_lines": total_comment_lines,
            "total_blank_lines": total_blank_lines,
            "comment_ratio": round(total_comment_lines / max(total_code_lines, 1), 4),
            "blank_ratio": round(total_blank_lines / max(total_lines, 1), 4),
            "average_file_size_bytes": round(avg_file_size, 1),
            "total_complexity": total_complexity,
            "extension_counts": extension_counts,
            "max_directory_depth": max_depth,
            "code_files_scanned": len(code_files),
        }

