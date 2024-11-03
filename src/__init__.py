"""Package untuk bot Telegram."""

# Level 1 - Core
from .bot_runner import BotRunner
from .config import CONFIG, DATA_DIR, GROUPS_FILE, MESSAGES_DIR
from .custom_types import (
    MessageSenderProtocol,
    SlowmodeInfo,
    StatusData,
    StatusManagerProtocol,
)
from .exceptions import AuthError, ConfigError, StatusError, TelegramError
from .keep_alive import keep_alive
from .logger import setup_logger

# Level 3 - Business Logic
from .message_sender import MessageSender
from .status_manager import StatusManager

# Level 2 - Services
from .telegram_client import TelegramClient

__all__ = [
    # Core
    "AuthError",
    "ConfigError",
    "StatusError",
    "TelegramError",
    "setup_logger",
    "MessageSenderProtocol",
    "StatusManagerProtocol",
    "SlowmodeInfo",
    "StatusData",
    "CONFIG",
    "DATA_DIR",
    "GROUPS_FILE",
    "MESSAGES_DIR",
    # Services
    "TelegramClient",
    "StatusManager",
    "keep_alive",
    # Business Logic
    "MessageSender",
    "BotRunner",
]
