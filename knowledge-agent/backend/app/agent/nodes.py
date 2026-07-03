"""
LangGraph node functions — each node transforms the agent state.
"""

import json

from langchain_aws import ChatBedrockConverse

from app.agent.actions import ACTION_REGISTRY, CRITICAL_ACTIONS
from app.core.config import settings
from app.core.logging import logger
from app.knowledge.vector_store import get_vector_store


def _get_llm() -> ChatBedrockConverse:
    """Create a Bedrock LLM client using Converse API."""
    return ChatBedrockConverse(
        model_id=settings.BEDROCK_MODEL_ID,
        region_name=settings.AWS_REGION,
        credentials_profile_name=None,
        temperature=0.3,
        max_tokens=1024,
    )


def retrieve_node(state: dict) -> dict:
    """Node 1: Retrieve relevant knowledge from the vector store."""
    query = state["query"]
    logger.info("[retrieve] Searching for: '%s'", query[:80])

    vector_store = get_vector_store()
    results = vector_store.retrieve(query, top_k=5)

    # Extract just the text content
    retrieved_docs = [r["content"] for r in results]
    distances = [r.get("distance") for r in results]

    # Filter out low-relevance results (distance threshold)
    if distances and all(d is not None for d in distances):
        # Lower distance = more relevant in ChromaDB
        filtered = [
            doc for doc, dist in zip(retrieved_docs, distances)
            if dist < 1.5  # threshold for relevance
        ]
        if filtered:
            retrieved_docs = filtered

    state["retrieved_docs"] = retrieved_docs
    logger.info("[retrieve] Found %d relevant documents", len(retrieved_docs))
    return state


def reason_node(state: dict) -> dict:
    """Node 2: LLM reasons over the query and retrieved documents."""
    query = state["query"]
    docs = state.get("retrieved_docs", [])
    memory = state.get("memory", [])

    logger.info("[reason] Reasoning over %d documents", len(docs))

    # Build context from retrieved docs
    if docs:
        context = "\n\n---\n\n".join(docs)
    else:
        context = "No relevant documents were found in the knowledge base."

    # Build memory context
    memory_context = ""
    if memory:
        memory_context = "\n\nPrevious conversation context:\n"
        for m in memory[-5:]:  # last 5 queries
            memory_context += f"- Q: {m['query']} → A: {m['action']}\n"

    prompt = (
        f"You are an intelligent knowledge agent. Analyze the following query and context.\n\n"
        f"Query: {query}\n\n"
        f"Retrieved Knowledge:\n{context}\n"
        f"{memory_context}\n\n"
        f"Provide a clear, concise reasoning about what the user is asking and what "
        f"information from the knowledge base is relevant. If no relevant information "
        f"was found, say so explicitly.\n\n"
        f"Reasoning:"
    )

    try:
        llm = _get_llm()
        response = llm.invoke(prompt)
        state["reasoning"] = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        logger.error("[reason] LLM call failed: %s", str(e))
        # Fallback reasoning when LLM is unavailable
        if docs:
            state["reasoning"] = (
                f"Based on {len(docs)} retrieved documents, the query '{query}' "
                f"appears to be about information available in our knowledge base. "
                f"Relevant content was found and can be used to provide an answer."
            )
        else:
            state["reasoning"] = (
                f"No relevant information was found in the knowledge base for the query: '{query}'. "
                f"The system cannot provide a knowledgeable answer."
            )

    logger.info("[reason] Reasoning complete (%d chars)", len(state["reasoning"]))
    return state


def decide_node(state: dict) -> dict:
    """Node 3: Decide which action to take based on reasoning."""
    query = state["query"]
    reasoning = state.get("reasoning", "")
    docs = state.get("retrieved_docs", [])

    logger.info("[decide] Choosing action...")

    available_actions = list(ACTION_REGISTRY.keys())

    prompt = (
        f"You are a decision-making agent. Based on the user's query and your reasoning, "
        f"pick exactly ONE action from this list:\n"
        f"{json.dumps(available_actions)}\n\n"
        f"Decision rules:\n"
        f"- 'answer_question': Use when the user asks a factual question and relevant data exists.\n"
        f"- 'generate_report': Use when the user asks for a summary, comparison, or overview.\n"
        f"- 'flag_issue': Use when the query reveals a potential problem or concern.\n"
        f"- 'no_action': Use when no relevant knowledge exists or the query is out of scope.\n\n"
        f"Query: {query}\n"
        f"Reasoning: {reasoning}\n"
        f"Number of relevant documents: {len(docs)}\n\n"
        f"Respond with ONLY the action name, nothing else.\n\n"
        f"Action:"
    )

    try:
        llm = _get_llm()
        response = llm.invoke(prompt)
        chosen = (response.content if hasattr(response, "content") else str(response)).strip().lower()

        # Validate the chosen action
        if chosen not in ACTION_REGISTRY:
            # Try to find a partial match
            for action in available_actions:
                if action in chosen:
                    chosen = action
                    break
            else:
                chosen = "answer_question" if docs else "no_action"
    except Exception as e:
        logger.error("[decide] LLM call failed: %s", str(e))
        # Fallback decision logic
        if not docs:
            chosen = "no_action"
        elif any(word in query.lower() for word in ["report", "summary", "overview", "list all", "compare"]):
            chosen = "generate_report"
        elif any(word in query.lower() for word in ["problem", "issue", "flag", "concern", "wrong", "block"]):
            chosen = "flag_issue"
        else:
            chosen = "answer_question"

    state["chosen_action"] = chosen

    # Check if this action requires approval
    state["require_approval"] = chosen in CRITICAL_ACTIONS

    logger.info("[decide] Chosen action: %s (approval: %s)", chosen, state["require_approval"])
    return state


def execute_node(state: dict) -> dict:
    """Node 4: Execute the chosen action."""
    action_name = state.get("chosen_action", "no_action")
    query = state["query"]
    docs = state.get("retrieved_docs", [])
    reasoning = state.get("reasoning", "")
    
    # Approval flow: skip execution if it requires approval but isn't approved
    if state.get("require_approval", False) and not state.get("is_approved", False):
        logger.info("[execute] Skipping execution — requires user approval for '%s'", action_name)
        state["result"] = f"Action '{action_name}' requires explicit user approval before execution."
        return state

    logger.info("[execute] Running action: %s", action_name)

    action_fn = ACTION_REGISTRY.get(action_name, ACTION_REGISTRY["no_action"])
    state["result"] = action_fn(query, docs, reasoning)

    logger.info("[execute] Action complete (%d chars result)", len(state["result"]))
    return state


def explain_node(state: dict) -> dict:
    """Node 5: Generate a human-readable explanation of the decision."""
    query = state["query"]
    action = state.get("chosen_action", "unknown")
    reasoning = state.get("reasoning", "")
    result = state.get("result", "")
    
    # If waiting for approval, provide a specific explanation
    if state.get("require_approval", False) and not state.get("is_approved", False):
        state["explanation"] = (
            f"I decided to run the '{action}' action because your query '{query}' "
            f"triggers a critical operation. For your security, this requires your explicit approval to proceed."
        )
        logger.info("[explain] Generated approval-required explanation")
        return state

    logger.info("[explain] Generating explanation...")

    prompt = (
        f"You are explaining your decision to a user. Write a brief, friendly explanation "
        f"(2-3 sentences) about why you chose the action '{action}' for their query.\n\n"
        f"Query: {query}\n"
        f"Action taken: {action}\n"
        f"Reasoning: {reasoning[:500]}\n\n"
        f"Explanation:"
    )

    try:
        llm = _get_llm()
        response = llm.invoke(prompt)
        state["explanation"] = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        logger.error("[explain] LLM call failed: %s", str(e))
        # Fallback explanation
        explanations = {
            "answer_question": f"I found relevant information in our knowledge base to answer your question about '{query}'.",
            "generate_report": f"Your query requested a summary or report, so I compiled the relevant data into a structured overview.",
            "flag_issue": f"Your query raised a potential concern that I've flagged for review.",
            "no_action": f"I couldn't find relevant information in our knowledge base for '{query}', so no specific action was taken.",
        }
        state["explanation"] = explanations.get(action, "The agent processed your query.")

    logger.info("[explain] Explanation complete")
    return state
