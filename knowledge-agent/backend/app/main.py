"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous Knowledge Execution Agent — AI-powered knowledge retrieval and action engine",
    version="1.0.0",
)

# ── CORS — allow the React dev server ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME}


logger.info("FastAPI app created — %s", settings.APP_NAME)
