from pathlib import Path
import zipfile


def extract_zip(zip_path: str, extract_to: str) -> str:
    """
    Extract a ZIP archive into a directory.

    Returns the extraction directory.
    """

    extract_path = Path(extract_to)

    extract_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    return str(extract_path)