
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # LLM
    gemini_api_key: str = ""
    llm_temperature: float = 0.0

    # Embedding
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Vector store
    chroma_persist_dir: str = "./vectorstore"

    # Retrieval
    top_k_docs: int = 5

    # Logging
    log_level: str = "INFO"

    # Paths
    data_dir: Path = Path("data")
    manuals_dir: Path = data_dir / "manuals"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()