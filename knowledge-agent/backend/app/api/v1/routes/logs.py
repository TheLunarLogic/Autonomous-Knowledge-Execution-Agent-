"""
GET /api/v1/logs — fetch recent audit log entries.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.log import AuditLogListResponse, AuditLogResponse
from app.services.audit_service import get_recent_logs

router = APIRouter()


@router.get(
    "/logs",
    response_model=AuditLogListResponse,
    summary="Get Audit Logs",
    description="Retrieve recent agent execution logs for auditing.",
)
async def list_logs(
    limit: int = Query(default=20, ge=1, le=100, description="Max entries to return"),
    session: AsyncSession = Depends(get_session),
) -> AuditLogListResponse:
    """Fetch paginated audit logs."""
    logs, total = await get_recent_logs(session, limit=limit)

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
    )
