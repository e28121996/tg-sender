"""Modul untuk konfigurasi aplikasi."""

import os
from pathlib import Path
from typing import Final, TypedDict

from .exceptions import ConfigError
from .logger import setup_logger

logger = setup_logger(name=__name__)


class ConfigDict(TypedDict):
    """Type untuk konfigurasi aplikasi."""

    API_ID: str
    API_HASH: str
    PHONE_NUMBER: str
    SESSION_STRING: str


# Konstanta untuk path
DATA_DIR: Final[Path] = Path("data")
GROUPS_FILE: Final[Path] = DATA_DIR / "groups.txt"
MESSAGES_DIR: Final[Path] = DATA_DIR / "messages"
STATUS_FILE: Final[Path] = DATA_DIR / "status.json"


def load_config() -> ConfigDict:
    """Load dan validasi konfigurasi dari environment.

    Untuk Replit, environment variables diambil dari Secrets tab.
    """
    # Replit environment variables - menggunakan nama yang sesuai dengan Secrets
    config: ConfigDict = {
        "API_ID": os.environ.get("API_ID", ""),  # Sesuai dengan nama di Secrets
        "API_HASH": os.environ.get("API_HASH", ""),  # Sesuai dengan nama di Secrets
        "PHONE_NUMBER": os.environ.get(
            "PHONE_NUMBER", ""
        ),  # Sesuai dengan nama di Secrets
        "SESSION_STRING": os.environ.get(
            "SESSION_STRING", ""
        ),  # Sesuai dengan nama di Secrets
    }

    # Validasi
    missing = [key for key, value in config.items() if not value]
    if missing:
        raise ConfigError(f"MISSING_ENV:{','.join(missing)}")

    # Convert API_ID ke integer
    try:
        config["API_ID"] = str(int(config["API_ID"]))  # Pastikan valid integer
    except ValueError as e:
        raise ConfigError("INVALID_API_ID") from e

    logger.info("✅ Konfigurasi berhasil diload")
    return config


# Export konfigurasi
CONFIG: Final[ConfigDict] = load_config()
