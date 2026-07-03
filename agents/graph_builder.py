"""
Assembles the LangGraph state graph.
"""
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes import entry_node, router, vision, planner, tool_caller, generator
import logging

logger = logging.getLogger(__name__)

# ------- helper to enforce dict return (optional safety) -------
def ensure_dict_return(node_func):
    """Wrapper that checks every node returns a dict."""
    def wrapped(state: AgentState):
        result = node_func(state)
        if not isinstance(result, dict):
            logger.error(f"Node {node_func.__name__} returned {type(result)} instead of dict")
            raise TypeError(f"Node '{node_func.__name__}' must return a dict, got {type(result).__name__}")
        return result
    return wrapped

# Wrap the vision node (already fixed in nodes.py, but keeps safety)
vision_safe = ensure_dict_return(vision)
# You can also wrap other nodes if you want

# ------- routing functions -------
def should_call_tool(state: AgentState) -> str:
    if state.get("tool_calls"):
        return "tool_caller"
    return "generator"

# ------- build graph -------
def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("entry", entry_node)           # new entry node
    workflow.add_node("vision", vision_safe)         # wrapped for safety
    workflow.add_node("planner", planner)
    workflow.add_node("tool_caller", tool_caller)
    workflow.add_node("generator", generator)

    # Entry point – now it's "entry"
    workflow.set_entry_point("entry")

    # Conditional edge from "entry" – uses router to decide next node
    workflow.add_conditional_edges(
        "entry",
        router,                   # returns "vision" or "planner"
        {
            "vision": "vision",
            "planner": "planner",
        }
    )

    # Vision always goes to planner
    workflow.add_edge("vision", "planner")

    # Planner decides: tool_caller or generator
    workflow.add_conditional_edges(
        "planner",
        should_call_tool,
        {
            "tool_caller": "tool_caller",
            "generator": "generator",
        }
    )

    # Tool caller loops back to planner
    workflow.add_edge("tool_caller", "planner")

    # Generator ends
    workflow.add_edge("generator", END)

    return workflow.compile()