from pathlib import Path

from app.engine.framework_detector import FrameworkDetector


IGNORE_DIRS = {
    ".git", ".github", "node_modules", ".venv", "venv", "env",
    "__pycache__", "dist", "build", ".next", ".cache", "coverage",
    ".pytest_cache", ".mypy_cache", ".idea", ".vscode", ".vs",
    "target", "bin", "obj", ".gradle", ".terraform",
}

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
    ".lock", ".map", ".swp", ".swo", ".DS_Store",
}

MAX_FILE_SIZE = 1_000_000  # 1MB


class ProjectScanner:

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def should_skip(self, path: Path):
        if any(part in IGNORE_DIRS for part in path.parts):
            return True
        ext = path.suffix.lower()
        if ext in SKIP_EXTENSIONS:
            return True
        try:
            if path.is_file() and path.stat().st_size > MAX_FILE_SIZE:
                return True
        except OSError:
            return True
        return False

    def detect_primary_language(self, extensions: dict):
        mapping = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".tsx": "TypeScript", ".jsx": "JavaScript", ".java": "Java",
            ".go": "Go", ".rs": "Rust", ".php": "PHP",
            ".cpp": "C++", ".c": "C", ".cs": "C#",
        }
        if not extensions:
            return "Unknown"
        top = max(extensions.items(), key=lambda x: x[1])[0]
        return mapping.get(top, top)

    def detect_repository_type(self, frameworks):
        frameworks = set(frameworks)
        if "React" in frameworks and (
            "FastAPI" in frameworks or "Flask" in frameworks
            or "Django" in frameworks or "Express" in frameworks
        ):
            return "Full Stack"
        if "React" in frameworks or "Next.js" in frameworks:
            return "Frontend"
        if ("FastAPI" in frameworks or "Flask" in frameworks
            or "Django" in frameworks or "Express" in frameworks):
            return "Backend API"
        return "Software Project"

    def scan(self):
        files = []
        for item in self.project_path.rglob("*"):
            if self.should_skip(item):
                continue
            if item.is_file():
                files.append(item)

        extensions = {}
        for file in files:
            suffix = file.suffix.lower()
            if suffix:
                extensions[suffix] = extensions.get(suffix, 0) + 1

        detector = FrameworkDetector(self.project_path)
        frameworks = detector.detect()

        return {
            "project_name": self.project_path.name,
            "total_files": len(files),
            "extensions": extensions,
            "frameworks": frameworks,
            "primary_language": self.detect_primary_language(extensions),
            "repository_type": self.detect_repository_type(frameworks),
            "framework_confidence": 100 if frameworks else 0,
            "has_readme": any(f.name.lower().startswith("readme") for f in files),
            "has_tests": any("test" in f.name.lower() for f in files),
            "has_docker": any(f.name == "Dockerfile" for f in files),
        }