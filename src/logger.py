"""Modul untuk setup logging."""

import logging
import sys
from typing import Final

# Format log dengan batasan panjang pesan untuk readability
LOG_FORMAT: Final[str] = "%(asctime)s - %(message).100s"
DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str) -> logging.Logger:
    """Setup logger dengan format standar."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
