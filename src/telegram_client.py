"""Modul untuk menangani operasi klien Telegram."""

from telethon import TelegramClient as BaseTelegramClient
from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    ChatGuestSendForbiddenError,
    ChatRestrictedError,
    ChatWriteForbiddenError,
    MessageNotModifiedError,
    MessageTooLongError,
    PeerIdInvalidError,
    SlowModeWaitError,
    UserBannedInChannelError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)
from telethon.errors import (
    FloodWaitError as TelethonFloodWaitError,
)

from .exceptions import AuthError, FloodWaitError
from .logger import setup_logger
from .status_manager import StatusManager

logger = setup_logger(__name__)


class TelegramClient:
    """Wrapper untuk klien Telegram."""

    def __init__(
        self,
        client: BaseTelegramClient,
        status_manager: StatusManager,
    ) -> None:
        """Inisialisasi TelegramClient."""
        self.client = client
        self.status = status_manager

    async def start(self) -> None:
        """Start client Telegram."""
        try:
            await self.client.start()
            logger.info("✅ Client Telegram started")
        except Exception as e:
            logger.error("❌ Error start client: %s", str(e))
            raise AuthError("Gagal start client") from e

    async def stop(self) -> None:
        """Stop client Telegram."""
        try:
            await self.client.disconnect()
            logger.info("✅ Client Telegram stopped")
        except Exception as e:
            logger.error("❌ Error stop client: %s", str(e))

    async def is_user_authorized(self) -> bool:
        """Cek apakah user sudah terautentikasi."""
        try:
            result = await self.client.is_user_authorized()
            return bool(result)
        except Exception as e:
            logger.error("❌ Error cek auth: %s", str(e))
            return False

    async def send_message(self, group: str, message: str) -> None:
        """Send message with specified error handling."""
        try:
            await self.client.send_message(group, message)
            logger.info("✅ Pesan terkirim ke %s", group)

        except (
            ChatWriteForbiddenError,
            UserBannedInChannelError,
            ChannelPrivateError,
            ChatAdminRequiredError,
            ChatRestrictedError,
            ChatGuestSendForbiddenError,
            PeerIdInvalidError,
            MessageTooLongError,
            MessageNotModifiedError,
            UsernameInvalidError,
            UsernameNotOccupiedError,
            ValueError,
        ) as e:
            reason = str(e).split("(")[0].strip()
            self.status.add_to_blacklist(group, reason)
            return

        except SlowModeWaitError as e:
            duration = int(str(e).split()[3])
            self.status.add_slowmode(group, duration)
            return

        except TelethonFloodWaitError as e:
            self.status.add_flood_wait(e.seconds)
            raise FloodWaitError(e.seconds) from e

        except Exception as e:
            if "CHAT_SEND_PLAIN_FORBIDDEN" in str(e):
                self.status.add_to_blacklist(group, str(e))
                return
            raise
