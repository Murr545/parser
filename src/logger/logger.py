import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(level: str = "INFO"):
    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join("logs", "bot.log")

    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] — %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8"
    )

    console_handler = logging.StreamHandler()

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[file_handler, console_handler],
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)