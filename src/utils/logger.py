"""Module untuk logging."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Membuat logger dengan format standar."""
    logger = logging.getLogger(name)

    if not logger.handlers and not logging.getLogger().handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
