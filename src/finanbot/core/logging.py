import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.finanbot.core.config import get_settings

settings = get_settings()

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s]: %(message)s"
LOG_LEVEL = getattr(logging, settings.log_level.upper(), logging.INFO)
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "finanbot.log"


def setup_logging() -> None:
    """Configure global logging behavior."""
    LOG_DIR.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a reusable logger for a given module."""
    return logging.getLogger(name)
