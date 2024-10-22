"""Modul konfigurasi untuk bot pengirim pesan Telegram."""

import logging
import os
from typing import Any, Dict

import yaml


class Config:
    def __init__(self) -> None:
        self.api_id: int = int(os.environ.get("TELEGRAM_API_ID", "0"))
        self.api_hash: str = os.environ.get("TELEGRAM_API_HASH", "")
        self.phone_number: str = os.environ.get("TELEGRAM_PHONE_NUMBER", "")
        if not self.phone_number:
            raise ValueError(
                "TELEGRAM_PHONE_NUMBER is not set in environment variables"
            )
        self.telegram_password: str = os.environ.get("TELEGRAM_2FA_PASSWORD", "")

        self.groups_file: str = os.environ.get("GROUPS_FILE", "data/groups.txt")
        self.message_files: list[str] = os.environ.get(
            "MESSAGE_FILES",
            "data/messages/template1.txt,data/messages/template2.txt,data/messages/template3.txt",
        ).split(",")
        self.status_file: str = os.environ.get("STATUS_FILE", "data/status.json")

        self.min_delay: float = float(os.environ.get("MIN_DELAY", "3.0"))
        self.max_delay: float = float(os.environ.get("MAX_DELAY", "5.0"))
        self.interval: Dict[str, float] = {
            "min": float(os.environ.get("INTERVAL_MIN", "1.1")),
            "max": float(os.environ.get("INTERVAL_MAX", "1.3")),
        }

        self.logging: Dict[str, Any] = {
            "file": os.environ.get("LOG_FILE", "logs/bot.log"),
            "level": os.environ.get("LOG_LEVEL", "INFO"),
        }

        self.messaging: Dict[str, Any] = {
            "batch_size": int(os.environ.get("BATCH_SIZE", "4")),
            "intra_batch_delay": {
                "min": float(os.environ.get("INTRA_BATCH_DELAY_MIN", "3.0")),
                "max": float(os.environ.get("INTRA_BATCH_DELAY_MAX", "5.0")),
            },
            "inter_batch_delay": {
                "min": float(os.environ.get("INTER_BATCH_DELAY_MIN", "10.0")),
                "max": float(os.environ.get("INTER_BATCH_DELAY_MAX", "20.0")),
            },
        }

        self.retry: Dict[str, Any] = {
            "max_attempts": int(os.environ.get("RETRY_MAX_ATTEMPTS", "3")),
            "initial_delay": float(os.environ.get("RETRY_INITIAL_DELAY", "1.0")),
            "backoff_factor": float(os.environ.get("RETRY_BACKOFF_FACTOR", "2.0")),
        }

        self.rate_limiting: Dict[str, Any] = {
            "max_messages_per_minute": int(
                os.environ.get("MAX_MESSAGES_PER_MINUTE", "20")
            ),
            "time_window": int(os.environ.get("RATE_LIMIT_TIME_WINDOW", "60")),
        }

        self.error_handling: Dict[str, Any] = {
            "max_attempts": int(os.environ.get("ERROR_MAX_ATTEMPTS", "3")),
            "initial_delay": float(os.environ.get("ERROR_INITIAL_DELAY", "1.0")),
            "backoff_factor": float(os.environ.get("ERROR_BACKOFF_FACTOR", "2.0")),
        }

        self._load_yaml_config()

    def _load_yaml_config(self) -> None:
        yaml_config_path = os.environ.get("YAML_CONFIG_PATH", "config.yaml")
        if os.path.exists(yaml_config_path):
            with open(yaml_config_path, "r") as f:
                yaml_config = yaml.safe_load(f)

            # Update config attributes from YAML if they're not set in environment variables
            for key, value in yaml_config.items():
                if hasattr(self, key) and not os.environ.get(key.upper()):
                    setattr(self, key, value)
                    logging.debug(f"Updated config {key} from YAML: {value}")

        logging.info(f"Configuration loaded from {yaml_config_path}")


CONFIG = Config()
logging.info(f"Configuration initialized with {len(vars(CONFIG))} attributes")
