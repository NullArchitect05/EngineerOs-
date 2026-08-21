import json
from pathlib import Path


class FrameworkDetector:
    IGNORE_DIRS = {
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        "dist",
        "build",
        ".next",
        ".cache",
        "coverage",
    }

    def __init__(self, project_path: Path):
        self.project_path = project_path

    def detect(self):
        frameworks = set()

        package = self.project_path / "package.json"

        if package.exists():
            frameworks.add("Node.js")

            try:
                data = json.loads(package.read_text(encoding="utf-8"))

                deps = {}
                deps.update(data.get("dependencies", {}))
                deps.update(data.get("devDependencies", {}))

                names = {k.lower() for k in deps.keys()}

                if "react" in names:
                    frameworks.add("React")

                if "next" in names:
                    frameworks.add("Next.js")

                if "express" in names:
                    frameworks.add("Express")

                if "vite" in names:
                    frameworks.add("Vite")

                if "typescript" in names:
                    frameworks.add("TypeScript")

            except Exception:
                pass

        req = self.project_path / "requirements.txt"

        if req.exists():
            frameworks.add("Python")

            try:
                for line in req.read_text(encoding="utf-8").splitlines():

                    pkg = line.split("==")[0].strip().lower()

                    if pkg == "fastapi":
                        frameworks.add("FastAPI")

                    elif pkg == "flask":
                        frameworks.add("Flask")

                    elif pkg == "django":
                        frameworks.add("Django")

            except Exception:
                pass

        pyproject = self.project_path / "pyproject.toml"

        if pyproject.exists():
            frameworks.add("Python")

        cargo = self.project_path / "Cargo.toml"

        if cargo.exists():
            frameworks.add("Rust")

        gomod = self.project_path / "go.mod"

        if gomod.exists():
            frameworks.add("Go")

        composer = self.project_path / "composer.json"

        if composer.exists():
            frameworks.add("PHP")

        pom = self.project_path / "pom.xml"

        if pom.exists():
            frameworks.add("Java")

        gradle = self.project_path / "build.gradle"

        if gradle.exists():
            frameworks.add("Gradle")

        return sorted(frameworks)