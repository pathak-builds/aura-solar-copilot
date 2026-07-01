"""
Assembles the LangGraph state graph.
"""
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes import router, vision, planner, tool_caller, generator

def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("router", router)
    workflow.add_node("vision", vision)
    workflow.add_node("planner", planner)
    workflow.add_node("tool_caller", tool_caller)
    workflow.add_node("generator", generator)

    # Entry point
    workflow.set_entry_point("router")

    # Router edges
    workflow.add_conditional_edges(
        "router",
        router,  # this function returns the next node name string
        {
            "vision": "vision",
            "planner": "planner",
        }
    )

    # Vision always goes to planner
    workflow.add_edge("vision", "planner")

    # Planner decides next step: if tool_calls exist -> tool_caller; else -> generator
    def should_call_tool(state: AgentState) -> str:
        if state.get("tool_calls"):
            return "tool_caller"
        return "generator"

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