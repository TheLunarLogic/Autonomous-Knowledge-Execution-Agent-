"""
Response schema for audit log entries.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Single audit log entry returned by GET /logs."""

    id: UUID
    query: str
    reasoning: str | None = None
    chosen_action: str | None = None
    result: str | None = None
    explanation: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Paginated list of audit logs."""

    logs: list[AuditLogResponse] = Field(default_factory=list)
    total: int = 0
