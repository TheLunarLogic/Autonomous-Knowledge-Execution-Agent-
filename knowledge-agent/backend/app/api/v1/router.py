"""
API v1 router — combines all v1 route modules.
"""

from fastapi import APIRouter

from app.api.v1.routes.ask import router as ask_router
from app.api.v1.routes.logs import router as logs_router

v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

v1_router.include_router(ask_router)
v1_router.include_router(logs_router)
