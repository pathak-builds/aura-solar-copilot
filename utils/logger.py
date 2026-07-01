import logging
import sys
from rich.logging import RichHandler
from config import settings

def setup_logging():
    """Configure structured, colourful logging for the entire application."""
    logging.basicConfig(
        level=settings.log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_time=False)]
    )
    # Reduce noise from some libraries
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)