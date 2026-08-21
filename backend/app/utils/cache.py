import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional


CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def get_file_hash(file_path: str) -> str:
    """Compute MD5 hash of a file for caching."""
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def get_url_hash(url: str) -> str:
    """Compute MD5 hash of a URL for caching."""
    return hashlib.md5(url.encode()).hexdigest()


def get_cached_result(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached analysis result by key."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            return data
        except Exception:
            return None
    return None


def set_cached_result(cache_key: str, result: Dict[str, Any]) -> None:
    """Cache analysis result."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        cache_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except Exception:
        pass
