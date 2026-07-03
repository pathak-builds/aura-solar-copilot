# ☀️ Aura – AI Powered Solar O&M Copilot

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)
![LangGraph](https://img.shields.io/badge/Agent-LangGraph-orange)
![Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

**An intelligent assistant for field engineers maintaining a 234 MW Floating Solar Plant at Maithon Dam.**

Aura helps field teams:
- 🔍 Troubleshoot inverter faults and equipment failures
- 🖼️ Inspect floating platforms using uploaded images
- 📚 Retrieve exact maintenance procedures from technical manuals
- 📋 Generate structured, source‑cited maintenance reports

Built with **LangGraph**, **Google Gemini 2.5 Flash (free tier)**, **ChromaDB**, and **Streamlit** – completely local, free, and production‑ready.

---

## 📖 Table of Contents
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🏗 Architecture

```mermaid
graph TD
    UI[Streamlit Chat UI] -->|Text + Image| AG[Agent Graph Entry]
    AG --> ROUTER{Router Node}
    ROUTER -->|Text only| PLANNER[Planner Node]
    ROUTER -->|Image included| VISION[Gemini Vision Node]
    VISION --> PLANNER
    PLANNER --> MEM[Conversation Memory]
    PLANNER --> RET[RAG Retriever]
    RET -->|Top-k documents| PLANNER
    PLANNER --> TOOLS[Tool Calling]
    TOOLS -->|Structured JSON| PLANNER
    PLANNER --> GEN[Response Generator]
    GEN --> UI
    MEM -.-> PLANNER
    RET -.-> VEC[(ChromaDB)]