"""Modul untuk interaksi dengan Telegram."""

import asyncio
from typing import Final, cast

from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    ChatRestrictedError,
    ChatWriteForbiddenError,
    FloodWaitError,
    MessageNotModifiedError,
    MessageTooLongError,
    PeerIdInvalidError,
    SlowModeWaitError,
    UnauthorizedError,
    UserBannedInChannelError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)
from telethon.sessions import StringSession
from telethon.sync import TelegramClient as BaseTelegramClient

from .config import CONFIG
from .custom_types import TelegramClientProtocol
from .exceptions import AuthError, TelegramError
from .logger import setup_logger

logger = setup_logger(name=__name__)

# Tambah konstanta timeout
CONNECT_TIMEOUT: Final[int] = 30  # 30 detik
SEND_TIMEOUT: Final[int] = 15  # 15 detik


class TelegramClient(TelegramClientProtocol):
    """Wrapper untuk Telethon client."""

    def __init__(self) -> None:
        """Inisialisasi client."""
        self._client: BaseTelegramClient | None = None

    async def connect(self) -> None:
        """Connect dan validasi session."""
        try:
            session: StringSession = StringSession(CONFIG["SESSION_STRING"])
            api_id: int = int(CONFIG["API_ID"])
            api_hash: str = CONFIG["API_HASH"]

            client: BaseTelegramClient = BaseTelegramClient(
                session,
                api_id,
                api_hash,
                timeout=CONNECT_TIMEOUT,
            )
            await client.connect()

            if not await client.is_user_authorized():
                await self.disconnect()
                raise AuthError("Session string tidak valid")

            self._client = client
            logger.info("✅ Berhasil connect ke Telegram")

        except UnauthorizedError as e:
            await self.disconnect()
            raise AuthError("Session string tidak valid") from e
        except Exception as e:
            connect_error: str = str(e)
            await self.disconnect()
            raise TelegramError(f"Error saat connect: {connect_error}") from e

    async def disconnect(self) -> None:
        """Disconnect dari Telegram."""
        if self._client:
            try:
                await self._client.disconnect()
                logger.info("✅ Berhasil disconnect dari Telegram")
            except Exception as e:
                disconnect_error: str = str(e)
                logger.error("❌ Error saat disconnect: %s", disconnect_error)
            finally:
                self._client = None

    def _validate_client(self) -> None:
        """Validasi client sudah diinisialisasi."""
        if not self._client:
            raise TelegramError("Client belum diinisialisasi")

    async def send_message(self, chat: str, message: str) -> None:
        """Kirim pesan ke grup."""
        self._validate_client()
        client = cast(BaseTelegramClient, self._client)

        try:
            await asyncio.wait_for(
                client.send_message(chat, message), timeout=SEND_TIMEOUT
            )
        except TimeoutError as err:
            raise TelegramError(f"Timeout setelah {SEND_TIMEOUT} detik") from err

        except (
            ChatWriteForbiddenError,
            UserBannedInChannelError,
            ChannelPrivateError,
            ChatAdminRequiredError,
            UsernameInvalidError,
            UsernameNotOccupiedError,
            ChatRestrictedError,
            PeerIdInvalidError,
            MessageTooLongError,
            MessageNotModifiedError,
            ValueError,
        ) as err:
            permission_error: str = str(err)
            raise TelegramError(f"Permission error: {permission_error}") from err

        except SlowModeWaitError as err:
            slowmode_duration: float = float(err.seconds)
            raise TelegramError(f"Slowmode error: {slowmode_duration}") from err

        except FloodWaitError as err:
            flood_duration: float = float(err.seconds)
            raise TelegramError(f"Flood wait error: {flood_duration}") from err

        except Exception as err:
            send_error: str = str(err)
            raise TelegramError(f"Send error: {send_error}") from err
