from typing import TypedDict, List, Optional, Any
from langchain_core.documents import Document

class AgentState(TypedDict):
    # User inputs
    user_query: str                    # latest text query from the user
    image_path: Optional[str]          # path to uploaded image, if any

    # Intermediate results
    image_analysis: Optional[str]      # textual description from vision node
    retrieved_docs: List[Document]     # documents from RAG
    tool_calls: Optional[List[dict]]   # requested tool calls from LLM (name, args)
    tool_results: Optional[List[dict]] # results from executed tools (name, result_json)

    # Final
    final_response: Optional[str]      # the structured maintenance guide

    # Memory
    messages: List[dict]               # full conversation history (role, content)