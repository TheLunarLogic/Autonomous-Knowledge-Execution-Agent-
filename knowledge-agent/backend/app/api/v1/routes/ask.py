"""
POST /api/v1/ask — run the agent and return the result.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.graph import run_agent
from app.core.logging import logger
from app.db.session import get_session
from app.schemas.query import QueryRequest, QueryResponse
from app.services.audit_service import save_audit_log

router = APIRouter()

# In-memory short-term memory (last 5 queries per session)
# In production, this would be per-user/session in Redis or DB
_memory: list[dict] = []
MAX_MEMORY = 5


@router.post(
    "/ask",
    response_model=QueryResponse,
    summary="Ask the Knowledge Agent",
    description="Submit a query to the autonomous agent. It retrieves knowledge, reasons, picks an action, executes it, and explains why.",
)
async def ask_agent(
    request: QueryRequest,
    session: AsyncSession = Depends(get_session),
) -> QueryResponse:
    """Run a query through the full agent pipeline."""
    global _memory

    logger.info("Received query: '%s' (approved: %s)", request.query[:80], request.is_approved)

    # Run the agent graph
    result = await run_agent(
        query=request.query,
        memory=_memory,
        is_approved=request.is_approved
    )

    # Save to audit log
    await save_audit_log(session, result)

    # Update short-term memory
    _memory.append({
        "query": request.query,
        "action": result.get("chosen_action", ""),
    })
    if len(_memory) > MAX_MEMORY:
        _memory = _memory[-MAX_MEMORY:]

    return QueryResponse(
        answer=result.get("result", "No result generated."),
        action_taken=result.get("chosen_action", "no_action"),
        explanation=result.get("explanation", "No explanation available."),
        require_approval=result.get("require_approval", False),
    )
