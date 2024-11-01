"""Modul untuk menjalankan bot Telegram."""

from telethon import TelegramClient as BaseTelegramClient
from telethon.sessions import StringSession

from .config import CONFIG
from .exceptions import AuthError, TelegramError
from .logger import setup_logger
from .message_sender import MessageSender
from .status_manager import StatusManager
from .telegram_client import TelegramClient

logger = setup_logger(__name__)


class BotRunner:
    """Runner utama untuk bot Telegram."""

    def __init__(self) -> None:
        """Inisialisasi BotRunner."""
        self.status_manager = StatusManager()
        self.telegram_client: TelegramClient | None = None
        self.message_sender: MessageSender | None = None

    async def initialize(self) -> None:
        """Inisialisasi komponen bot sesuai spesifikasi."""
        try:
            # 1. Setup client dengan session string dari env
            base_client = BaseTelegramClient(
                StringSession(CONFIG["SESSION_STRING"]),
                CONFIG["API_ID"],
                CONFIG["API_HASH"],
            )

            # 2. Setup wrapper client dengan status manager
            telegram_client = TelegramClient(
                base_client,
                self.status_manager,
            )

            # 3. Start dan validasi sesi
            await telegram_client.start()

            if not await telegram_client.is_user_authorized():
                raise AuthError("User belum terautentikasi")

            # 4. Setup message sender
            self.telegram_client = telegram_client
            self.message_sender = MessageSender(
                telegram_client,
                self.status_manager,
            )

            logger.info("✅ Bot berhasil diinisialisasi")

        except Exception as e:
            await self.cleanup()
            raise TelegramError(f"Inisialisasi gagal: {e!s}") from e

    async def run(self) -> None:
        """Jalankan proses pengiriman pesan."""
        if not self.telegram_client or not self.message_sender:
            logger.error("❌ Bot belum diinisialisasi")
            return

        try:
            # Ambil daftar grup aktif (tidak blacklist/slowmode)
            groups = self.status_manager.get_active_groups()
            if not groups:
                logger.warning("⚠️ Tidak ada grup aktif")
                return

            # Proses pengiriman dalam batch
            await self.message_sender.send_messages_in_batches(groups)

        except Exception as e:
            logger.error("❌ Error: %s", str(e))
            raise

    async def cleanup(self) -> None:
        """Bersihkan resources."""
        try:
            if self.telegram_client:
                await self.telegram_client.stop()
        except Exception as e:
            logger.error("❌ Error cleanup: %s", str(e))
