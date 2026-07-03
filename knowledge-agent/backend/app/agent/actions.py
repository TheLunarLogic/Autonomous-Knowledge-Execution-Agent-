"""
Agent action functions — placeholder business logic.

Each function receives the query, retrieved docs, and reasoning,
then returns a formatted result string.
"""

from app.core.logging import logger


def answer_question(query: str, docs: list[str], reasoning: str) -> str:
    """Format a direct answer based on retrieved knowledge and reasoning."""
    logger.info("Action: answer_question for '%s'", query[:60])

    if not docs:
        return "I don't have enough information to answer this question accurately."

    return (
        f"Based on the available knowledge:\n\n"
        f"{reasoning}\n\n"
        f"Sources consulted: {len(docs)} knowledge items."
    )


def generate_report(query: str, docs: list[str], reasoning: str) -> str:
    """Generate a summary report from retrieved knowledge."""
    logger.info("Action: generate_report for '%s'", query[:60])

    if not docs:
        return "No data available to generate a report."

    report_lines = [
        "═══ GENERATED REPORT ═══",
        f"Query: {query}",
        f"Data Sources: {len(docs)} items analyzed",
        "",
        "Summary:",
        reasoning,
        "",
        "Key Findings:",
    ]

    for i, doc in enumerate(docs[:5], 1):
        # Truncate each doc for the report
        snippet = doc[:200] + "..." if len(doc) > 200 else doc
        report_lines.append(f"  {i}. {snippet}")

    report_lines.append("")
    report_lines.append("═══ END OF REPORT ═══")

    return "\n".join(report_lines)


def flag_issue(query: str, docs: list[str], reasoning: str) -> str:
    """Flag a potential issue found in the knowledge base."""
    logger.info("Action: flag_issue for '%s'", query[:60])

    return (
        f"⚠️  ISSUE FLAGGED\n"
        f"Query: {query}\n"
        f"Severity: MEDIUM\n"
        f"Details: {reasoning}\n"
        f"Affected items: {len(docs)}\n"
        f"Recommendation: Review the flagged items and take corrective action."
    )


def no_action(query: str, docs: list[str], reasoning: str) -> str:
    """No relevant action can be taken for this query."""
    logger.info("Action: no_action for '%s'", query[:60])

    return (
        f"No specific action is needed for this query.\n"
        f"Reason: {reasoning}"
    )


# Registry mapping action names to functions
ACTION_REGISTRY: dict[str, callable] = {
    "answer_question": answer_question,
    "generate_report": generate_report,
    "flag_issue": flag_issue,
    "no_action": no_action,
}

# Actions that require user approval before execution
CRITICAL_ACTIONS = {"flag_issue"}
