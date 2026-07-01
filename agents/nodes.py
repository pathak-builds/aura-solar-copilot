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

def router(state: AgentState) -> str:
    """Determine if image analysis is needed."""
    if state.get("image_path"):
        logger.info("Image detected – routing to vision node.")
        return "vision"
    logger.info("No image – routing directly to planner.")
    return "planner"

def vision(state: AgentState) -> AgentState:
    """Analyse uploaded image using Gemini Vision."""
    img_path = state["image_path"]
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
    # Always proceed to planner after vision
    return state

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

    # 2. Build messages list (conversation history + latest)
    messages = state.get("messages", [])[-6:]  # keep last 6 turns for context
    # Add latest user query (with image info if present)
    user_content = query
    messages.append({"role": "user", "content": user_content})

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
        # This will route to generator (we can just end or go to generator for formatting)
        return state

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

def generator(state: AgentState) -> AgentState:
    """Final formatting node (can be used for post-processing if needed)."""
    # In this implementation, planner already sets final_response, so we just pass through.
    # Could add citation formatting or additional checks here.
    logger.info("Generator node: final response ready.")
    return state