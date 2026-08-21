from pathlib import Path


IGNORE_DIRS = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    ".next",
    ".cache",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
}


class RepositoryParser:
    """
    Safely parses a repository into reusable metadata.
    Every analysis module should consume this parser
    instead of scanning the filesystem itself.
    """

    def __init__(self, root: str):
        self.root = Path(root)

    def should_ignore(self, path: Path) -> bool:
        return any(part in IGNORE_DIRS for part in path.parts)

    def get_all_files(self):

        files = []

        for item in self.root.rglob("*"):

            if self.should_ignore(item):
                continue

            if item.is_file():
                files.append(item)

        return files

    def get_extensions(self):

        extensions = {}

        for file in self.get_all_files():

            ext = file.suffix.lower()

            if ext:

                extensions[ext] = (
                    extensions.get(ext, 0) + 1
                )

        return extensions

    def manifest_files(self):

        manifests = []

        targets = {
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
            "composer.json",
            "Dockerfile",
            "docker-compose.yml",
        }

        for file in self.get_all_files():

            if file.name in targets:

                manifests.append(file)

        return manifests

    def total_files(self):

        return len(self.get_all_files())

    def total_directories(self):

        dirs = []

        for item in self.root.rglob("*"):

            if item.is_dir():

                if self.should_ignore(item):
                    continue

                dirs.append(item)

        return len(dirs)