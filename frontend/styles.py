
import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    /* Main page background */
    .stApp {
        background-color: #0E1117;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #00C853 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Chat message bubbles */
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #1F2937;
    }
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: #0A1F14;
        border-left: 4px solid #00C853;
    }
    /* Buttons */
    .stButton>button {
        background-color: #00C853;
        color: #000000;
        border-radius: 8px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #00E676;
    }
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
    }
    /* Code blocks */
    pre {
        background-color: #1F2937;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #30363D;
    }
    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #00C853;
    }
    </style>
    """, unsafe_allow_html=True)