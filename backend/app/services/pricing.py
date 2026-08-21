"""Simple scan-based pricing tracker.
Tracks scans by IP/session and enforces free tier limits.
For production, replace with a proper database & Stripe integration.
"""
import json
import os
import hashlib
from pathlib import Path
from typing import Dict, Optional

PRICING_DIR = Path("pricing_data")
PRICING_DIR.mkdir(exist_ok=True)
DATA_FILE = PRICING_DIR / "scan_tracker.json"


def _load_data() -> Dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_data(data: Dict):
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def _get_client_id(request) -> str:
    """Generate a stable ID for a client (IP-based)."""
    forwarded = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "unknown"
    return hashlib.md5(client_ip.encode()).hexdigest()[:12]


def get_free_scan_limit() -> int:
    return int(os.getenv("FREE_SCAN_LIMIT", "3"))


def get_monthly_price() -> float:
    return float(os.getenv("PRICE_PER_MONTH", "5.99"))


def check_scan_allowed(request) -> Dict:
    """Check if client can scan. Returns {'allowed': bool, 'remaining': int, 'is_paid': bool}."""
    client_id = _get_client_id(request)
    data = _load_data()
    client_info = data.get(client_id, {"scan_count": 0, "is_paid": False})
    limit = get_free_scan_limit()

    if client_info.get("is_paid"):
        return {"allowed": True, "remaining": -1, "is_paid": True, "client_id": client_id}

    used = client_info.get("scan_count", 0)
    remaining = limit - used
    if remaining <= 0:
        return {"allowed": False, "remaining": 0, "is_paid": False, "client_id": client_id}

    return {"allowed": True, "remaining": remaining, "is_paid": False, "client_id": client_id}


def increment_scan_count(request) -> int:
    """Increment scan count for a client. Returns new count."""
    client_id = _get_client_id(request)
    data = _load_data()
    client_info = data.get(client_id, {"scan_count": 0, "is_paid": False})
    client_info["scan_count"] = client_info.get("scan_count", 0) + 1
    data[client_id] = client_info
    _save_data(data)
    return client_info["scan_count"]


def get_client_status(request) -> Dict:
    """Get full status for a client (for pricing page)."""
    client_id = _get_client_id(request)
    data = _load_data()
    client_info = data.get(client_id, {"scan_count": 0, "is_paid": False})
    limit = get_free_scan_limit()
    return {
        "scan_count": client_info.get("scan_count", 0),
        "free_limit": limit,
        "remaining": max(0, limit - client_info.get("scan_count", 0)),
        "is_paid": client_info.get("is_paid", False),
        "monthly_price": get_monthly_price(),
        "client_id": client_id,
    }
