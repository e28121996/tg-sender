"""Modul untuk mengirim pesan ke grup."""

import asyncio
import random
from typing import Final

from .config import MESSAGES_DIR
from .custom_types import MessageSenderProtocol
from .exceptions import TelegramError
from .logger import setup_logger
from .status_manager import StatusManager
from .telegram_client import TelegramClient

logger = setup_logger(name=__name__)

# Konstanta untuk pengiriman pesan
BATCH_SIZE: Final[int] = 4  # Jumlah pesan per batch
MESSAGE_DELAY: Final[tuple[int, int]] = (2, 6)  # Interval 4±2 detik
MAX_ERROR_LENGTH: Final[int] = 200  # Panjang maksimal pesan error


class MessageSender(MessageSenderProtocol):
    """Class untuk mengirim pesan ke grup."""

    def __init__(self, client: TelegramClient, status: StatusManager) -> None:
        """Inisialisasi message sender.

        Args:
            client: Instance TelegramClient
            status: Instance StatusManager
        """
        self.client = client
        self.status = status
        self._templates: list[str] = []
        self._load_templates()

    def _load_templates(self) -> None:
        """Load template pesan dari folder messages.

        Raises:
            TelegramError: Jika tidak ada template yang valid
        """
        try:
            # Validasi folder template
            if not MESSAGES_DIR.exists() or not MESSAGES_DIR.is_dir():
                raise TelegramError(f"Folder {MESSAGES_DIR} tidak valid")

            # Load semua file .txt
            message_files = list(MESSAGES_DIR.glob("*.txt"))
            if not message_files:
                raise TelegramError("Tidak ada template pesan")

            # Load isi file
            for file in message_files:
                content = file.read_text().strip()
                if content:
                    self._templates.append(content)

            if not self._templates:
                raise TelegramError("Semua template pesan kosong")

            logger.info("✅ Berhasil load %d template pesan", len(self._templates))

        except Exception as e:
            raise TelegramError(f"Error saat load template: {e}") from e

    def get_random_template(self) -> str:
        """Get template pesan random.

        Returns:
            str: Template pesan yang dipilih secara random

        Raises:
            TelegramError: Jika tidak ada template pesan
        """
        if not self._templates:
            raise TelegramError("Tidak ada template pesan")
        return random.choice(self._templates)

    async def send_batch(self, groups: list[str]) -> None:
        """Kirim pesan ke batch grup."""
        if not groups:
            return  # Skip jika tidak ada grup

        success: int = 0
        failed: int = 0

        for group in groups:
            try:
                # Pilih template random untuk setiap grup
                template: str = self.get_random_template()
                await self.send_message(group, template)
                success += 1

                # Delay hanya jika masih ada grup berikutnya
                if group != groups[-1]:
                    delay: float = random.uniform(MESSAGE_DELAY[0], MESSAGE_DELAY[1])
                    await asyncio.sleep(delay)

            except TelegramError as e:
                failed += 1
                error_msg = self._format_error_message(str(e))
                logger.error("❌ Error saat kirim ke %s: %s", group, error_msg)

        logger.info("📊 Hasil batch - Sukses: %d, Gagal: %d", success, failed)

    async def send_message(self, chat: str, message: str) -> None:
        """Kirim pesan ke grup.

        Args:
            chat: ID atau username grup
            message: Pesan yang akan dikirim

        Raises:
            TelegramError: Jika ada error saat mengirim pesan
        """
        try:
            await self.client.send_message(chat, message)
            logger.info("✅ Berhasil kirim pesan ke %s", chat)

        except TelegramError as e:
            error_msg = self._format_error_message(str(e))
            raise TelegramError(f"Error saat kirim pesan: {error_msg}") from e

    def _format_error_message(self, error: str) -> str:
        """Format pesan error agar konsisten dan tidak terpotong."""
        # Ekstrak error type dan detail
        parts = error.split(":", 1)
        error_type = parts[0].strip()
        error_detail = parts[1].strip() if len(parts) > 1 else ""

        # Format pesan error
        if error_detail:
            full_message = f"{error_type}: {error_detail}"
        else:
            full_message = error_type

        # Truncate jika terlalu panjang
        if len(full_message) > MAX_ERROR_LENGTH:
            return (
                f"{error_type}: {error_detail[:MAX_ERROR_LENGTH-len(error_type)-5]}..."
            )

        return full_message
