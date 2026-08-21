from fastapi import APIRouter

from app.api.routes.upload import router as upload_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes.results import router as results_router
from app.api.routes.github import router as github_router
from app.api.routes.compare import router as compare_router
from app.api.routes.ai_analysis import router as ai_router
from app.api.routes.report import router as report_router
from app.api.routes.pricing import router as pricing_router

api_router = APIRouter()

api_router.include_router(upload_router, prefix="/upload", tags=["Upload"])
api_router.include_router(analyze_router, prefix="/analyze", tags=["Analyze"])
api_router.include_router(results_router, prefix="/results", tags=["Results"])
api_router.include_router(github_router, prefix="/analyze/github", tags=["GitHub"])
api_router.include_router(compare_router, prefix="/compare", tags=["Compare"])
api_router.include_router(ai_router, prefix="/analyze/ai", tags=["AI Analysis"])
api_router.include_router(report_router, prefix="/report", tags=["Report"])
api_router.include_router(pricing_router, prefix="/pricing", tags=["Pricing"])