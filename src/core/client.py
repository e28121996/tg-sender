from collections.abc import Awaitable
from typing import Any

from telethon import TelegramClient as TelethonClient
from telethon.sessions import StringSession
from telethon.types import Message

from ..utils.config import get_env
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ClientError(Exception):
    """Base error untuk client Telegram."""


class ResponseError(ClientError):
    """Response dari server tidak valid."""


class AuthError(ClientError):
    """Error saat autentikasi."""


class DisconnectError(ClientError):
    """Error saat disconnect dari Telegram."""


class TelegramClient:
    """Wrapper untuk Telethon client dengan type hints."""

    def __init__(self) -> None:
        """Inisialisasi client dengan kredensial."""
        self.api_id = int(get_env("TELEGRAM_API_ID"))
        self.api_hash = get_env("TELEGRAM_API_HASH")
        self.session = get_env("TELEGRAM_SESSION")
        self._client: Any = None
        self._connected = False

    def _handle_auth_error(self) -> None:
        """Menangani error autentikasi."""
        self._connected = False
        self._client = None
        raise AuthError()

    async def start(self) -> None:
        """Memulai koneksi client Telegram."""
        try:
            if self._client and self._connected:
                return

            client = TelethonClient(
                StringSession(self.session), self.api_id, self.api_hash
            )
            await client.connect()

            if await client.is_user_authorized():
                self._client = client
                self._connected = True
                logger.info("Client berhasil login")
            else:
                self._handle_auth_error()
        except Exception as e:
            logger.error("Error saat memulai client: %s", str(e))
            self._connected = False
            self._client = None
            raise ClientError() from e

    async def send_message(self, group_url: str, message: str) -> Message:
        """Mengirim pesan ke grup."""
        if not self._client or not self._connected:
            try:
                await self.start()
            except Exception as e:
                logger.error("Gagal memulai ulang client: %s", str(e))
                raise ClientError() from e

        try:
            result = await self._client.send_message(group_url, message)
        except Exception as e:
            if "Connection" in str(e):
                self._connected = False
            logger.error("Error saat kirim pesan: %s", str(e))
            raise
        else:
            if not isinstance(result, Message):
                raise ResponseError()
            return result

    async def disconnect(self) -> None:
        """Memutuskan koneksi client."""
        if not self._client:
            return

        try:
            result = await self._client.disconnect()
            if isinstance(result, Awaitable):
                await result
        except Exception as e:
            logger.error("Error saat disconnect: %s", str(e))
            raise DisconnectError() from e
        finally:
            self._client = None
            self._connected = False
