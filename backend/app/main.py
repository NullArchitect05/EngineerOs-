import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

# Load .env from backend root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="EngineerOS API",
    version="1.1.0",
    description="Repository Analysis Engine — with AI-powered insights"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "EngineerOS API Running",
        "version": "1.1.0",
        "status": "success",
        "ai_enabled": bool(os.getenv("LLM_API_KEY") and os.getenv("LLM_API_KEY") != "sk-or-v1-your-free-openrouter-key-here"),
    }