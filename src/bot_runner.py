"""Modul untuk menjalankan bot."""

import asyncio
import random
from typing import Final

from .logger import setup_logger
from .message_sender import MessageSender
from .status_manager import StatusManager
from .telegram_client import TelegramClient

logger = setup_logger(name=__name__)

# Konstanta untuk pengiriman pesan
BATCH_SIZE: Final[int] = 4  # Jumlah pesan per batch
BATCH_DELAY: Final[tuple[int, int]] = (13, 17)  # Interval 15±2 detik


class BotRunner:
    """Class untuk menjalankan bot."""

    def __init__(self) -> None:
        """Inisialisasi bot runner."""
        self.client = TelegramClient()
        self.status = StatusManager()
        self.sender = MessageSender(self.client, self.status)

    async def initialize(self) -> None:
        """Inisialisasi koneksi dan validasi."""
        try:
            await self.client.connect()
            logger.info("✅ Bot berhasil diinisialisasi")
        except Exception as e:
            logger.error("❌ Error saat inisialisasi bot: %s", str(e))
            await self.client.disconnect()
            raise

    async def run(self) -> None:
        """Jalankan bot."""
        try:
            # Cleanup slowmode sebelum mulai
            self.status.cleanup_expired_slowmode()

            # Get active groups
            active_groups = self.status.get_active_groups()
            total = len(self.status.get_groups())
            blacklisted = len(self.status.get_blacklist())
            slowmode = len(self.status.get_slowmode())
            active = len(active_groups)

            logger.info(
                "📊 Statistik - Total: %d, Blacklist: %d, Slowmode: %d, Aktif: %d",
                total,
                blacklisted,
                slowmode,
                active,
            )

            # Proses per batch
            for i in range(0, len(active_groups), BATCH_SIZE):
                batch: list[str] = active_groups[i : i + BATCH_SIZE]
                logger.info(
                    "📦 Memproses batch %d/%d",
                    i // BATCH_SIZE + 1,
                    -(-len(active_groups) // BATCH_SIZE),
                )
                await self.sender.send_batch(batch)

                if i + BATCH_SIZE < len(active_groups):
                    delay: float = random.uniform(BATCH_DELAY[0], BATCH_DELAY[1])
                    await asyncio.sleep(delay)

        except Exception as e:
            logger.error("❌ Error saat jalankan bot: %s", str(e))
            raise

        finally:
            await self.client.disconnect()
