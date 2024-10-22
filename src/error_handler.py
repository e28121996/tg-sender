"""Modul untuk menangani kesalahan dalam bot pengirim pesan Telegram."""

import asyncio
from typing import Any, Callable

from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    ChatWriteForbiddenError,
    SlowModeWaitError,
    UserBannedInChannelError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)

from .config import CONFIG
from .logger import setup_logger
from .status_manager import StatusManager

logger = setup_logger(__name__, CONFIG.logging["file"])


class ErrorHandler:
    def __init__(self, status_manager: StatusManager) -> None:
        self.status_manager = status_manager
        self.max_attempts = CONFIG.error_handling["max_attempts"]
        self.initial_delay = CONFIG.error_handling["initial_delay"]
        self.backoff_factor = CONFIG.error_handling["backoff_factor"]
        logger.info("ErrorHandler diinisialisasi")

    async def handle_error(self, error: Exception, group: str) -> None:
        if isinstance(error, SlowModeWaitError):
            await self._handle_slowmode_error(error, group)
        elif self._should_blacklist(error):
            await self._handle_blacklist_error(error, group)
        else:
            await self._handle_generic_error(error, group)

    def _should_blacklist(self, error: Exception) -> bool:
        blacklist_errors = (
            ChannelPrivateError,
            ChatAdminRequiredError,
            ChatWriteForbiddenError,
            UserBannedInChannelError,
            UsernameInvalidError,
            UsernameNotOccupiedError,
        )
        return isinstance(error, blacklist_errors) or any(
            err_msg in str(error)
            for err_msg in [
                "You're banned from sending messages",
                "Cannot find any entity corresponding to",
                "CHAT_SEND_PLAIN_FORBIDDEN",
                "No user has",  # Untuk kasus username tidak valid
            ]
        )

    async def _handle_slowmode_error(
        self, error: SlowModeWaitError, group: str
    ) -> None:
        duration: int = (
            error.seconds if hasattr(error, "seconds") else 3600
        )  # Default 1 jam jika tidak ada informasi durasi
        self.status_manager.add_to_slowmode(group, duration)
        logger.warning(f"Slowmode aktif untuk grup {group} selama {duration} detik")

    async def _handle_blacklist_error(self, error: Exception, group: str) -> None:
        self.status_manager.add_to_blacklist(group)
        error_type = type(error).__name__
        logger.error(f"Kesalahan {error_type} untuk grup {group}: {error}")
        logger.info(f"Grup {group} ditambahkan ke blacklist karena {error_type}")

    async def _handle_generic_error(self, error: Exception, group: str) -> None:
        logger.error(f"Kesalahan umum untuk grup {group}: {error}")

    async def retry_with_backoff(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_attempts - 1:
                    raise
                delay: float = self.initial_delay * (self.backoff_factor**attempt)
                logger.warning(
                    f"Percobaan {attempt + 1} gagal: {e}. Mencoba lagi dalam {delay:.2f} detik."
                )
                await asyncio.sleep(delay)
