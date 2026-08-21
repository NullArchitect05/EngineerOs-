"""Pricing and usage tracking routes."""
from fastapi import APIRouter, Request
from app.services.pricing import check_scan_allowed, increment_scan_count, get_client_status

router = APIRouter()


@router.get("/status")
async def pricing_status(request: Request):
    """Get the current client's usage status and pricing info."""
    status = get_client_status(request)
    return status


@router.get("/check")
async def check_access(request: Request):
    """Check if the client can perform a scan."""
    result = check_scan_allowed(request)
    return result


@router.post("/increment")
async def increment_scan(request: Request):
    """Increment scan count for the client."""
    count = increment_scan_count(request)
    return {"scan_count": count}
