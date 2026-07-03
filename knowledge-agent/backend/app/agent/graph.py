"""
LangGraph state machine — orchestrates the agent's reasoning pipeline.

Flow: retrieve → reason → decide_action → execute → explain
"""

from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    decide_node,
    execute_node,
    explain_node,
    reason_node,
    retrieve_node,
)
from app.core.logging import logger


class AgentState(TypedDict):
    """Typed state passed through the LangGraph pipeline."""

    query: str
    retrieved_docs: list[str]
    reasoning: str
    chosen_action: str
    result: str
    explanation: str
    require_approval: bool
    is_approved: bool
    memory: list[dict]  # short-term memory — last N queries


def build_agent_graph() -> StateGraph:
    """Construct and compile the agent state graph."""
    graph = StateGraph(AgentState)

    # ── Add nodes ─────────────────────────────────────────────
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("reason", reason_node)
    graph.add_node("decide", decide_node)
    graph.add_node("execute", execute_node)
    graph.add_node("explain", explain_node)

    # ── Define edges (linear pipeline) ────────────────────────
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "reason")
    graph.add_edge("reason", "decide")
    graph.add_edge("decide", "execute")
    graph.add_edge("execute", "explain")
    graph.add_edge("explain", END)

    logger.info("Agent graph built: retrieve → reason → decide → execute → explain")
    return graph.compile()


# Compiled graph singleton
agent_graph = build_agent_graph()


async def run_agent(query: str, memory: list[dict] | None = None, is_approved: bool = False) -> dict:
    """Run a query through the full agent pipeline.

    Args:
        query: The user's natural language question.
        memory: Optional list of previous query/action pairs for context.
        is_approved: True if the user has explicitly approved this critical action execution.

    Returns:
        Final agent state dict with all fields populated.
    """
    initial_state: AgentState = {
        "query": query,
        "retrieved_docs": [],
        "reasoning": "",
        "chosen_action": "",
        "result": "",
        "explanation": "",
        "require_approval": False,
        "is_approved": is_approved,
        "memory": memory or [],
    }

    logger.info("Running agent for query: '%s'", query[:80])
    result = agent_graph.invoke(initial_state)
    logger.info(
        "Agent complete — action: %s, approval: %s",
        result.get("chosen_action"),
        result.get("require_approval"),
    )
    return result
