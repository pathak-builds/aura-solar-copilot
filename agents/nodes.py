"""
LangGraph node implementations.
"""
import logging
import json
from typing import Dict, Any, List
from langchain_core.documents import Document
from agents.state import AgentState
from utils.llm import GeminiProvider
from prompts.system_prompts import SYSTEM_PROMPT
from tools.definitions import TOOL_DEFINITIONS
from tools.solar_tools import (
    calculate_tilt_anomaly,
    calculate_power_loss,
    calculate_generation_loss,
    weather_risk,
    generate_compliance_ticket,
    estimate_repair_priority,
)
from rag.chain import retrieve_context
from config import settings

logger = logging.getLogger(__name__)

# Instantiate provider once
llm = GeminiProvider()

# Map tool names to actual functions
TOOL_MAP = {
    "calculate_tilt_anomaly": calculate_tilt_anomaly,
    "calculate_power_loss": calculate_power_loss,
    "calculate_generation_loss": calculate_generation_loss,
    "weather_risk": weather_risk,
    "generate_compliance_ticket": generate_compliance_ticket,
    "estimate_repair_priority": estimate_repair_priority,
}

# ---------- Helper to enforce dict return ----------
def ensure_dict(func):
    """Decorator that checks the node returns a dict."""
    def wrapper(state: AgentState) -> AgentState:
        result = func(state)
        if not isinstance(result, dict):
            logger.error(f"Node {func.__name__} returned {type(result)} instead of dict")
            raise TypeError(
                f"Node '{func.__name__}' must return a dict, got {type(result).__name__}"
            )
        return result
    return wrapper

# ---------- Node: entry (does nothing, just passes state) ----------
def entry_node(state: AgentState) -> AgentState:
    """
    Simple entry node. It does not change the state.
    The conditional edge after this node decides where to go.
    """
    logger.info("Entry node – routing to vision or planner.")
    return state

# ---------- Conditional edge function (NOT a node) ----------
def router(state: AgentState) -> str:
    """
    Determine if image analysis is needed.
    Returns the name of the next node: "vision" or "planner".
    """
    if state.get("image_path"):
        logger.info("Image detected – routing to vision node.")
        return "vision"
    logger.info("No image – routing directly to planner.")
    return "planner"

# ---------- Node: vision ----------
@ensure_dict
def vision(state: AgentState) -> AgentState:
    """Analyse uploaded image using Gemini Vision."""
    img_path = state.get("image_path")
    if not img_path:
        logger.warning("Vision node called but no image_path in state.")
        state["image_analysis"] = "No image provided."
        return state

    prompt = (
        "You are a solar O&M expert. Describe the image in detail, focusing on any anomalies, "
        "damage (cracks, corrosion, burn marks, bird droppings, vegetation, tilt), or safety issues. "
        "Provide a technical description suitable for an engineer."
    )
    try:
        description = llm.generate_vision(img_path, prompt)
        logger.info("Image analysis complete.")
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        description = "Image analysis failed. Please ensure the image is valid."

    state["image_analysis"] = description
    return state

# ---------- Node: planner ----------
# ---------- Node: planner ----------
@ensure_dict
def planner(state: AgentState) -> AgentState:
    """
    Core reasoning node.
    Retrieves context, builds a prompt WITH documents, calls LLM.
    """
    # 1. Retrieve relevant documents
    query = state["user_query"]
    if state.get("image_analysis"):
        query += f"\n\n[Image context: {state['image_analysis']}]"
    docs, sources_str = retrieve_context(query, settings.top_k_docs)
    state["retrieved_docs"] = docs

    # 2. Build the user prompt – INCLUDE the documents
    if docs:
        context = "\n\n".join(
            [f"DOCUMENT {i+1} (source: {d.metadata.get('source', 'unknown')}):\n{d.page_content}"
             for i, d in enumerate(docs)]
        )
        full_user_content = f"""CONTEXT DOCUMENTS:
{context}

USER QUERY:
{state["user_query"]}"""
        if state.get("image_analysis"):
            full_user_content += f"\n\nImage Analysis: {state['image_analysis']}"
    else:
        full_user_content = query

    # 3. Build messages (conversation history + this enriched user message)
    messages = state.get("messages", [])[-6:]  # keep last 6 turns
    messages.append({"role": "user", "content": full_user_content})

    # 4. Call LLM with tools
    try:
        response = llm.generate_text(
            system_prompt=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOL_DEFINITIONS
        )
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        state["final_response"] = f"Error communicating with AI model: {str(e)}"
        return state

    # 5. Handle tool call vs final answer
    if hasattr(response, "function_call") and response.function_call:
        tool_call = response.function_call
        logger.info(f"LLM requested tool: {tool_call.name}")
        state["tool_calls"] = [{"name": tool_call.name, "args": dict(tool_call.args)}]
    else:
        final_text = response.text if hasattr(response, "text") else str(response)
        state["final_response"] = final_text

    return state

# ---------- Node: tool_caller ----------
@ensure_dict
def tool_caller(state: AgentState) -> AgentState:
    """Execute tool calls requested by the LLM."""
    results = []
    for call in state.get("tool_calls", []):
        func_name = call["name"]
        args = call["args"]
        func = TOOL_MAP.get(func_name)
        if not func:
            result = {"error": f"Unknown tool: {func_name}"}
        else:
            try:
                result_json = func(**args)
                result = {"name": func_name, "result": result_json}
            except Exception as e:
                result = {"name": func_name, "error": str(e)}
        results.append(result)

    state["tool_results"] = results
    # Convert tool results into a message to feed back to the planner
    tool_msg = "Tool execution results:\n" + "\n".join(
        [json.dumps(r, indent=2) for r in results]
    )
    state.setdefault("messages", []).append({"role": "tool", "content": tool_msg})
    logger.info("Tools executed, routing back to planner.")
    return state

# ---------- Node: generator ----------
@ensure_dict
def generator(state: AgentState) -> AgentState:
    """Final formatting node (can be used for post-processing if needed)."""
    # In this implementation, planner already sets final_response, so we just pass through.
    # Could add citation formatting or additional checks here.
    logger.info("Generator node: final response ready.")
    return state