"""
Request and response schemas for the /ask endpoint.
"""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Incoming user query."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's natural language question",
        examples=["What wireless headphones do you have?"],
    )


class QueryResponse(BaseModel):
    """Agent's full response to a query."""

    answer: str = Field(..., description="The agent's answer or action result")
    action_taken: str = Field(..., description="Which action the agent chose")
    explanation: str = Field(..., description="Why the agent chose this action")
    require_approval: bool = Field(
        default=False,
        description="True if the action is critical and needs user confirmation",
    )
