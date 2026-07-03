"""
Streamlit page layout and main application logic.
"""
import streamlit as st
import time
from config import settings
from frontend.styles import apply_styles
from frontend.chat_interface import init_chat, display_chat, add_user_message, add_assistant_message
from agents.graph_builder import build_graph
from agents.state import AgentState
from utils.logger import setup_logging
from pathlib import Path
import tempfile
import os

setup_logging()  # initialise structured logging

def configure_sidebar() -> dict:
    """Sidebar controls; returns a dict of user settings."""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/solar-panel.png", width=80)
        st.title("Aura Copilot")

        api_key = st.text_input(
            "Gemini API Key",
            value=settings.gemini_api_key or "",
            type="password",
            help="Free from Google AI Studio"
        )
        temperature = st.slider("LLM Temperature", 0.0, 1.0, settings.llm_temperature, 0.1)
        top_k = st.slider("Retrieved Documents", 1, 10, settings.top_k_docs)

        st.markdown("---")
        st.subheader("Knowledge Base")
        if st.button("🔄 Re‑ingest Manuals"):
            with st.spinner("Re‑ingesting documents..."):
                from ingestion.ingest import run_ingestion
                run_ingestion()
            st.success("Ingestion complete!")

        st.markdown("---")
        st.subheader("About")
        st.markdown("""
        **Aura** is an AI copilot for field engineers at  
        Maithon Dam 234 MW Floating Solar Plant.
        """)
        st.markdown("Made with ❤️ for Renewable Energy")

        return {
            "api_key": api_key,
            "temperature": temperature,
            "top_k": top_k
        }

def run_agent(query: str, image_path: str | None, ui_settings: dict) -> dict:
    """
    Execute the LangGraph agent with the user's query, image, and settings.
    Returns the final state dict.
    """
    from config import settings
    import os

    # Update settings with values from sidebar (fall back to existing if empty)
    if ui_settings["api_key"]:
        os.environ["GEMINI_API_KEY"] = ui_settings["api_key"]
        settings.gemini_api_key = ui_settings["api_key"]
    settings.llm_temperature = ui_settings.get("temperature", settings.llm_temperature)
    settings.top_k_docs = ui_settings.get("top_k", settings.top_k_docs)

    # Build the compiled graph
    graph = build_graph()

    # Prepare state
    initial_state: AgentState = {
        "user_query": query,
        "image_path": image_path,
        "image_analysis": None,
        "retrieved_docs": [],
        "tool_calls": None,
        "tool_results": None,
        "final_response": None,
        "messages": []
    }

    # Add recent conversation history from UI into the agent's memory
    ui_history = st.session_state.messages[-6:]
    agent_messages = []
    for msg in ui_history:
        if msg["role"] in ("user", "assistant"):
            agent_messages.append({"role": msg["role"], "content": msg["content"]})
    initial_state["messages"] = agent_messages

    # Invoke
    start_time = time.perf_counter()
    final_state = graph.invoke(initial_state)
    elapsed = time.perf_counter() - start_time

    # Add elapsed time to state for display
    final_state["elapsed_time"] = f"{elapsed:.2f} s"
    return final_state

def display_results(state: dict):
    """Show final answer, sources, tool calls, etc."""
    if state.get("final_response"):
        add_assistant_message(state["final_response"])
    else:
        add_assistant_message("⚠️ No response generated. Please try again.")

    if "elapsed_time" in state:
        st.caption(f"⏱️ Response time: {state['elapsed_time']}")

    with st.expander("🔍 Agent Steps & Debug Info", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Image Analysis:**")
            if state.get("image_analysis"):
                st.info(state["image_analysis"])
            else:
                st.caption("No image provided.")
        with col2:
            st.markdown("**Tool Calls:**")
            if state.get("tool_calls"):
                st.json(state["tool_calls"])
            else:
                st.caption("No tools called.")

        st.markdown("**Retrieved Sources:**")
        if state.get("retrieved_docs"):
            for i, doc in enumerate(state["retrieved_docs"], 1):
                src = doc.metadata.get("source", "unknown")
                snippet = doc.page_content[:200].replace("\n", " ")
                st.markdown(f"**[{i}] {src}**  \n{snippet}...")
        else:
            st.caption("No documents retrieved.")

        if state.get("tool_results"):
            st.markdown("**Tool Results:**")
            st.json(state["tool_results"])

def main():
    st.set_page_config(
        page_title="Aura – Solar O&M Copilot",
        page_icon="☀️",
        layout="wide"
    )
    apply_styles()
    init_chat()

    user_settings = configure_sidebar()

    chat_container = st.container()
    with chat_container:
        display_chat()

    col1, col2 = st.columns([8, 2])
    with col1:
        user_input = st.chat_input("Describe the problem (e.g., 'Inverter showing E-008 fault...')")
    with col2:
        uploaded_file = st.file_uploader(
            "Upload image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

    if user_input:
        image_path = None
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                image_path = tmp.name

        add_user_message(user_input, image_path)

        with st.spinner("🧠 Aura is analysing..."):
            try:
                final_state = run_agent(
                    query=user_input,
                    image_path=image_path,
                    ui_settings=user_settings          
                )
                display_results(final_state)
            except Exception as e:
                add_assistant_message(f"❌ **Error:** {str(e)}")

        if image_path and os.path.exists(image_path):
            os.unlink(image_path)

if __name__ == "__main__":
    main()