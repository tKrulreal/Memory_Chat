from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict, total=False):
    """State schema cho LangGraph agent.

    Mỗi node đọc và ghi vào state này.
    total=False cho phép tất cả fields là optional.
    """

    # Base fields
    query: str
    context: dict  # Dict với user_id, contact_id, conversation_id
    analysis: str
    response: str
    error: str
    metadata: dict

    # Orchestrator fields
    intent: str  # SEARCH, MEMORY, RECOMMENDATION, CHITCHAT, etc.
    intent_confidence: float
    intent_reasoning: str
    context_data: str  # Built context string cho LLM
    tools_to_call: list[str]  # List of tool names
    agent_responses: dict  # tool_name -> result
    execution_summary: str  # Tổng hợp tất cả tool results
    is_valid: bool  # Validation result
    validation_result: str  # Validation reason if invalid
    final_response: str  # Response cuối cùng
