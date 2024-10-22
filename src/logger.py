"""Modul untuk konfigurasi logging."""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Dict

from .config import CONFIG

# Simpan referensi ke semua logger yang telah dibuat
loggers: Dict[str, logging.Logger] = {}


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Set up logger dengan nama dan file log yang diberikan."""
    # Jika logger sudah ada, kembalikan logger yang ada
    if name in loggers:
        return loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Hapus semua handler yang mungkin sudah ada
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Pastikan direktori log ada
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Gunakan RotatingFileHandler untuk membatasi ukuran file log
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.info(f"Logger {name} set up with file handler for {log_file}")

    # Nonaktifkan propagasi untuk menghindari log ganda
    logger.propagate = False

    # Simpan referensi ke logger
    loggers[name] = logger

    return logger


# Konfigurasi root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Hapus semua handler yang ada pada root logger
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Tambahkan RotatingFileHandler ke root logger
root_file_handler = RotatingFileHandler(
    CONFIG.logging["file"], maxBytes=10 * 1024 * 1024, backupCount=5
)
root_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
root_file_handler.setFormatter(root_formatter)
root_logger.addHandler(root_file_handler)

# Nonaktifkan propagasi untuk logger telethon
logging.getLogger("telethon").propagate = False


def setup_main_logger() -> logging.Logger:
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        CONFIG.logging["file"], maxBytes=10 * 1024 * 1024, backupCount=5
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(f"Main logger set up with file handler for {CONFIG.logging['file']}")
    return logger


main_logger = setup_main_logger()


def get_logger(module_name: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(main_logger, {"name": module_name})
