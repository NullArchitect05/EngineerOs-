from pathlib import Path


def get_all_files(project_path: str):
    """
    Return every file inside a project.
    """

    return [
        str(path)
        for path in Path(project_path).rglob("*")
        if path.is_file()
    ]


def get_python_files(project_path: str):
    """
    Return only Python files.
    """

    return [
        str(path)
        for path in Path(project_path).rglob("*.py")
    ]