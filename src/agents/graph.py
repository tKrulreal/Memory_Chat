"""
Legacy graph.py — backward compatibility wrapper.

Sử dụng AssistantOrchestrator mới bên trong.
Giữ interface cũ: analyze + respond nodes.
"""

from langgraph.graph import END, StateGraph

from src.agents.nodes.example_node import analyze_node
from src.agents.nodes.example_node import respond_node as legacy_respond_node
from src.agents.orchestrator import (
    AgentState,
    Intent,
    respond_node,
    run_copilot,
)

# Re-export for backward compat
__all__ = ["build_graph", "agent", "analyze_node", "respond_node", "run_copilot", "Intent"]


def should_continue(state: AgentState) -> str:
    """Route based on whether an error occurred during analysis."""
    if state.get("error"):
        return END
    return "respond"


def build_graph() -> StateGraph:
    """Legacy build_graph — keeps analyze + respond nodes for backward compat."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("analyze", analyze_node)
    graph.add_node("respond", legacy_respond_node)

    # Add edges
    graph.set_entry_point("analyze")
    graph.add_conditional_edges("analyze", should_continue)
    graph.add_edge("respond", END)

    return graph.compile()


# Legacy agent instance (for routes.py)
agent = build_graph()
