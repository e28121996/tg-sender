"""Modul untuk setup logging."""

import logging
import sys
from typing import Final

# Konstanta logging
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message).100s"
DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL: Final[int] = logging.INFO

# Emoji untuk status
SUCCESS_EMOJI: Final[str] = "✅"  # Centang hijau untuk success
ERROR_EMOJI: Final[str] = "🔴"  # Lingkaran merah untuk error
WARNING_EMOJI: Final[str] = "🔸"  # Warning sign untuk warning
INFO_EMOJI: Final[str] = "📝"  # Memo untuk info

# Cache untuk logger yang sudah dibuat
_loggers: dict[str, logging.Logger] = {}


def setup_logger(name: str) -> logging.Logger:
    """Setup logger dengan format standar.

    Args:
        name: Nama logger, biasanya __name__

    Returns:
        logging.Logger: Logger yang sudah dikonfigurasi

    Notes:
        - Logger di-cache untuk menghindari duplicate handlers
        - Format: timestamp - module - level - message
        - Message dipotong max 100 karakter
        - Output ke stdout
    """
    # Return dari cache jika sudah ada
    if name in _loggers:
        return _loggers[name]

    # Buat logger baru
    logger: logging.Logger = logging.getLogger(name)

    # Skip jika sudah ada handler
    if logger.handlers:
        _loggers[name] = logger
        return logger

    # Setup formatter
    formatter: logging.Formatter = logging.Formatter(
        fmt=LOG_FORMAT, datefmt=DATE_FORMAT
    )

    # Setup handler
    handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Setup logger
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    logger.propagate = False  # Hindari duplicate logs

    # Simpan ke cache
    _loggers[name] = logger

    return logger
