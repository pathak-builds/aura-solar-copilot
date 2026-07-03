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
    Retrieves context, builds a prompt, calls LLM (with tools if needed).
    Decides next step: tool_caller or generator.
    """
    # 1. Retrieve relevant documents
    query = state["user_query"]
    if state.get("image_analysis"):
        query += f" [Image context: {state['image_analysis']}]"
    docs, sources_str = retrieve_context(query, settings.top_k_docs)
    state["retrieved_docs"] = docs

    # 2. Build messages list (conversation history + latest query)
    # Get last 6 messages from UI history (stored in state)
    history = state.get("messages", [])[-6:]
    messages = []
    # Append system prompt as a system message (if your provider supports it)
    # Since our llm.py builds a single prompt, we can just add it as a user message
    # or we can rely on the system_prompt parameter.
    # We'll put the system prompt separately in the call, so we only put user/assistant/tool here.
    for msg in history:
        # Ensure we have the correct role names: 'user', 'assistant', 'tool'
        role = msg.get("role", "user")
        # Map 'assistant' to 'assistant' (our llm.py will treat it as assistant)
        # For 'tool', we keep it as 'tool'
        messages.append({"role": role, "content": msg.get("content", "")})
    # Add the current user query (with image context)
    messages.append({"role": "user", "content": query})

    # 3. Call LLM with tools
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

    # 4. Safely parse response
    # Expected response is a genai.types.GenerateContentResponse
    if hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, "content") and candidate.content.parts:
            parts = candidate.content.parts
            for part in parts:
                # Check for function call
                if hasattr(part, "function_call") and part.function_call:
                    tool_call = part.function_call
                    logger.info(f"LLM requested tool: {tool_call.name} with args {tool_call.args}")
                    state["tool_calls"] = [{"name": tool_call.name, "args": dict(tool_call.args)}]
                    return state
                # Check for text
                elif hasattr(part, "text") and part.text:
                    final_text = part.text
                    state["final_response"] = final_text
                    return state
            # If we reach here, no usable part found
            state["final_response"] = "LLM returned an empty or unsupported response."
            return state
        else:
            state["final_response"] = "LLM response missing content."
            return state
    else:
        # Fallback for simplified response objects (e.g., if using a different wrapper)
        if hasattr(response, "function_call") and response.function_call:
            tool_call = response.function_call
            state["tool_calls"] = [{"name": tool_call.name, "args": dict(tool_call.args)}]
            return state
        elif hasattr(response, "text") and response.text:
            state["final_response"] = response.text
            return state
        else:
            state["final_response"] = f"Unexpected LLM response format: {type(response)}"
            return state

    # 4. Check for function call
    if hasattr(response, "function_call") and response.function_call:
        tool_call = response.function_call
        logger.info(f"LLM requested tool: {tool_call.name} with args {tool_call.args}")
        state["tool_calls"] = [{"name": tool_call.name, "args": dict(tool_call.args)}]
        # We'll return the state and the conditional edge will route to tool_caller
        return state
    else:
        # No tool requested – final answer directly
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