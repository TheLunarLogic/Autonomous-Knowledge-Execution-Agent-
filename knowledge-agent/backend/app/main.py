"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.core.config import settings
from app.core.logging import logger
from app.db.session import engine
from app.db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Starting %s ...", settings.APP_NAME)

    # Create database tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created")

    yield

    # Shutdown
    await engine.dispose()
    logger.info("Database connections closed")


app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous Knowledge Execution Agent — AI-powered knowledge retrieval and action engine",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — allow the React dev server ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────
app.include_router(v1_router)


@app.get("/health", tags=["system"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME}


# ── Knowledge loading endpoint ────────────────────────────────
@app.post("/api/v1/load-knowledge", tags=["system"])
async def load_knowledge():
    """Load sample data into PostgreSQL and ChromaDB."""
    from app.db.session import AsyncSessionLocal
    from app.knowledge.loader import load_csv, load_json

    data_dir = Path(__file__).parent.parent / "data"

    async with AsyncSessionLocal() as session:
        json_count = await load_json(session, data_dir / "sample.json")
        csv_count = await load_csv(session, data_dir / "sample.csv")
        await session.commit()

    return {
        "status": "loaded",
        "json_items": json_count,
        "csv_items": csv_count,
    }


logger.info("FastAPI app created — %s", settings.APP_NAME)
