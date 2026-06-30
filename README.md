graph TD
    UI[Streamlit UI] -->|Text + Image| AG[Agent Graph Entry]
    AG --> ROUTER{Router Node}
    ROUTER -->|Text only| PLANNER[Planner Node]
    ROUTER -->|Image included| VISION[Gemini Vision Node]
    VISION --> PLANNER
    PLANNER --> MEM[Conversation Memory]
    PLANNER --> RET[RAG Retriever]
    RET -->|Top-k docs| PLANNER
    PLANNER --> TOOLS[Tool Calling]
    TOOLS -->|Structured JSON| PLANNER
    PLANNER --> GEN[Response Generator]
    GEN --> UI
    MEM -.-> PLANNER
    RET -.-> VEC[(ChromaDB)]

    