"""Modul untuk setup logging."""

import logging
import os
import sys
from typing import Final

# Format log sesuai environment
HEROKU_FORMAT: Final = "%(message).100s"  # Batasi panjang pesan ke 100 karakter
LOCAL_FORMAT: Final = "%(asctime)s - %(message).100s"  # Format detail dengan batasan
DATE_FORMAT: Final = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str) -> logging.Logger:
    """Setup logger berdasarkan environment."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    is_heroku = bool(os.getenv("DYNO"))
    formatter = logging.Formatter(
        fmt=HEROKU_FORMAT if is_heroku else LOCAL_FORMAT,
        datefmt=DATE_FORMAT,
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
