"""Modul untuk interaksi dengan Telegram."""

import asyncio
from typing import Any, Final, TypeAlias

from telethon import TelegramClient as BaseTelegramClient
from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    ChatRestrictedError,
    ChatWriteForbiddenError,
    ForbiddenError,
    UnauthorizedError,
    UserBannedInChannelError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)
from telethon.sessions import StringSession

from .config import CONFIG
from .custom_types import TelegramClientProtocol
from .exceptions import AuthError, TelegramError
from .logger import (
    setup_logger,
)
from .status_manager import StatusManager

logger = setup_logger(name=__name__)

# Konstanta timeout dan durasi
CONNECT_TIMEOUT: Final[int] = 30
SEND_TIMEOUT: Final[int] = 15
SECONDS_PER_MINUTE: Final[int] = 60

# Type alias untuk client
TelethonClient: TypeAlias = Any  # noqa: UP040


def _raise_auth_error(error: str, original_error: Exception | None = None) -> None:
    """Raise auth error."""
    if original_error:
        raise AuthError(error) from original_error
    raise AuthError(error) from None


def _raise_telegram_error(error: str, original_error: Exception | None = None) -> None:
    """Raise telegram error."""
    if original_error:
        raise TelegramError(error) from original_error
    raise TelegramError(error) from None


class TelegramClient(TelegramClientProtocol):
    """Class untuk interaksi dengan Telegram."""

    def __init__(self, status_manager: StatusManager) -> None:
        """Initialize telegram client."""
        api_id = int(CONFIG["API_ID"])
        self._client: TelethonClient = BaseTelegramClient(
            StringSession(CONFIG["SESSION_STRING"]),
            api_id,
            CONFIG["API_HASH"],
        )
        self.status = status_manager

    def _validate_client(self) -> TelethonClient:
        """Validasi client sudah diinisialisasi."""
        if self._client is None:
            _raise_telegram_error(TelegramError.CLIENT_UNINITIALIZED)
        return self._client

    async def connect(self) -> None:
        """Connect ke Telegram."""
        retries = 3
        retry_delay = 5  # seconds
        last_error = None

        for attempt in range(retries):
            try:
                client = self._validate_client()

                # Tambah timeout yang lebih lama
                await asyncio.wait_for(
                    client.connect(),
                    timeout=30.0,  # 30 detik timeout
                )

                if not await client.is_user_authorized():
                    _raise_auth_error(AuthError.SESSION_INVALID)

            except UnauthorizedError as e:
                _raise_auth_error(AuthError.AUTH_FAILED.format(str(e)), e)

            except TimeoutError:
                last_error = "Connection timeout"
                if attempt < retries - 1:
                    logger.warning(
                        f"⚠️ Connect timeout (attempt {attempt + 1}/{retries}), "
                        f"retry dalam {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)
                continue

            except Exception as e:
                last_error = str(e)
                if attempt < retries - 1:
                    logger.warning(
                        f"⚠️ Connect error (attempt {attempt + 1}/{retries}): {e}, "
                        f"retry dalam {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)
                continue
            else:
                logger.info("✅ Berhasil connect ke Telegram")
                return

        # Jika semua retry gagal
        raise TelegramError.connect_error(last_error or "Unknown error")

    async def disconnect(self) -> None:
        """Disconnect dari Telegram."""
        try:
            client = self._validate_client()
            result = client.disconnect()
            if result is not None:
                await result
        except Exception:
            logger.exception("Error saat disconnect")

    async def send_message(self, chat: str, message: str) -> None:
        """Kirim pesan ke grup."""
        try:
            client = self._validate_client()
            entity = await client.get_entity(chat)
            await asyncio.wait_for(client.send_message(entity, message), SEND_TIMEOUT)

        except Exception as e:
            error_str = str(e).lower()

            # Deteksi slowmode harus lebih spesifik
            slowmode_patterns = [
                r"slow[\s_-]*mode.*?(\d+)",  # slow mode, slowmode
                r"wait.*?(\d+).*?second",  # wait X seconds
                r"flood.*?(\d+)",  # flood wait X
                r"too fast.*?(\d+)",  # too fast, wait X
                r"retry in (\d+)",  # retry in X seconds
            ]

            import re

            for pattern in slowmode_patterns:
                if match := re.search(pattern, error_str):
                    duration = float(match.group(1))
                    logger.warning(
                        f"⏳ {chat} - SLOWMODE {self._format_duration(int(duration))}"
                    )
                    self.status.add_slowmode(chat, duration)
                    return

            # Jika bukan slowmode, handle error lainnya
            if isinstance(e, UsernameNotOccupiedError | UsernameInvalidError):
                logger.warning(f"⛔ {chat} - USERNAME_INVALID")
                self.status.add_to_blacklist(chat, "USERNAME_INVALID")
                raise TelegramError("USERNAME_INVALID") from None

            if isinstance(
                e,
                ChatWriteForbiddenError
                | UserBannedInChannelError
                | ChannelPrivateError
                | ChatAdminRequiredError
                | ChatRestrictedError
                | ForbiddenError,
            ):
                error_type = e.__class__.__name__.replace("Error", "").upper()
                logger.warning(f"⛔ {chat} - {error_type}")
                self.status.add_to_blacklist(chat, error_type)
                raise TelegramError(error_type) from None

            # Error lainnya yang tidak teridentifikasi
            logger.warning(f"⛔ {chat} - SEND_ERROR")
            self.status.add_to_blacklist(chat, "SEND_ERROR")
            raise TelegramError("SEND_ERROR") from None

    def _format_duration(self, seconds: float) -> str:
        """Format durasi dalam format yang konsisten."""
        seconds_int = int(seconds)
        if seconds_int < SECONDS_PER_MINUTE:
            return f"{seconds_int}s"
        minutes = seconds_int // SECONDS_PER_MINUTE
        hours = minutes // 60
        if hours > 0:
            return f"{hours}h {minutes % 60}m"
        return f"{minutes}m"
