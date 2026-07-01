from agents.graph_builder import build_graph
from agents.state import AgentState

def test_routing_text_only():
    state = AgentState(
        user_query="Inverter error E-008",
        image_path=None,
        messages=[],
        image_analysis=None,
        retrieved_docs=[],
        tool_calls=None,
        tool_results=None,
        final_response=None
    )
    graph = build_graph()
    # We just want to check that router returns 'planner'
    result = graph.invoke(state)
    # If no error, it's a good sign. We'll check that final_response is not empty.
    assert "final_response" in result
    assert result["final_response"] is not None