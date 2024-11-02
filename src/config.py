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

    Returns:
        ConfigDict: Konfigurasi yang sudah divalidasi

    Raises:
        ConfigError: Jika ada environment variable yang tidak valid
    """
    try:
        config: ConfigDict = {
            "API_ID": os.getenv("API_ID", ""),
            "API_HASH": os.getenv("API_HASH", ""),
            "PHONE_NUMBER": os.getenv("PHONE_NUMBER", ""),
            "SESSION_STRING": os.getenv("SESSION_STRING", ""),
        }

        # Validasi nilai tidak kosong
        missing = [key for key, value in config.items() if not value]
        if missing:
            raise ConfigError(
                f"Environment variables tidak lengkap: {', '.join(missing)}"
            )

        logger.info("✅ Konfigurasi berhasil diload")
        return config

    except Exception as e:
        raise ConfigError(f"Error saat load konfigurasi: {e}") from e


# Load config saat import
CONFIG: Final[ConfigDict] = load_config()
