"""
Streamlit chat management utilities.
"""
import streamlit as st
from typing import Optional, List, Dict

def init_chat():
    """Initialize chat history in session state if not present."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Welcome message from assistant
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👷‍♂️ Aura ready. Describe the issue or upload an image for analysis."
        })

def display_chat():
    """Render all previous messages."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def add_user_message(text: str, image_path: Optional[str] = None):
    """Add a user message to history and display it."""
    if image_path:
        # If image, we can display the image and the text
        content = f"{text}\n\n![Uploaded Image]({image_path})"
    else:
        content = text
    st.session_state.messages.append({"role": "user", "content": content})
    with st.chat_message("user"):
        st.markdown(content)

def add_assistant_message(text: str):
    """Add assistant message to history and display."""
    st.session_state.messages.append({"role": "assistant", "content": text})
    with st.chat_message("assistant"):
        st.markdown(text)