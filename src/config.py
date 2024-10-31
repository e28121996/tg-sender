"""Modul untuk konfigurasi dari environment variables."""

import os
from typing import TypedDict

from .exceptions import ConfigError


class Config(TypedDict):
    """Format konfigurasi."""

    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str
    SESSION_STRING: str


def load_config() -> Config:
    """Load konfigurasi dari environment variables.

    Returns:
        Config: Dictionary berisi konfigurasi

    Raises:
        ConfigError: Jika ada environment variable yang tidak lengkap
    """
    # Cek environment variables yang diperlukan
    required = ["API_ID", "API_HASH", "PHONE_NUMBER", "SESSION_STRING"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise ConfigError(f"Environment variables tidak lengkap: {', '.join(missing)}")

    # Validasi API_ID harus berupa angka
    try:
        api_id = int(os.environ["API_ID"])
    except ValueError as e:
        raise ConfigError("API_ID harus berupa angka") from e

    # Return config yang sudah divalidasi
    return {
        "API_ID": api_id,
        "API_HASH": os.environ["API_HASH"],
        "PHONE_NUMBER": os.environ["PHONE_NUMBER"],
        "SESSION_STRING": os.environ["SESSION_STRING"],
    }


# Load config sekali saat import
CONFIG = load_config()
