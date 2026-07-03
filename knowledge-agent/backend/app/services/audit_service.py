"""
Audit service — read/write audit logs to PostgreSQL.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.models import AuditLog


async def save_audit_log(session: AsyncSession, agent_state: dict) -> AuditLog:
    """Insert an agent execution into the audit_logs table.

    Args:
        session: Active async database session.
        agent_state: Final state dict from the agent graph.

    Returns:
        The created AuditLog record.
    """
    log_entry = AuditLog(
        query=agent_state.get("query", ""),
        reasoning=agent_state.get("reasoning", ""),
        chosen_action=agent_state.get("chosen_action", ""),
        result=agent_state.get("result", ""),
        explanation=agent_state.get("explanation", ""),
    )
    session.add(log_entry)
    await session.flush()
    await session.refresh(log_entry)

    logger.info("Audit log saved: %s (action: %s)", log_entry.id, log_entry.chosen_action)
    return log_entry


async def get_recent_logs(session: AsyncSession, limit: int = 20) -> tuple[list[AuditLog], int]:
    """Fetch the most recent audit log entries.

    Args:
        session: Active async database session.
        limit: Maximum number of entries to return.

    Returns:
        Tuple of (list of AuditLog entries, total count).
    """
    # Get total count
    total_result = await session.execute(select(func.count(AuditLog.id)))
    total = total_result.scalar_one()

    # Get recent logs ordered by creation time
    result = await session.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    logs = list(result.scalars().all())

    logger.info("Fetched %d audit logs (total: %d)", len(logs), total)
    return logs, total
