"""Modul untuk mengirim pesan ke grup."""

import asyncio
import random
from collections.abc import Sequence

from .exceptions import FloodWaitError
from .logger import setup_logger
from .status_manager import StatusManager
from .telegram_client import TelegramClient

logger = setup_logger(__name__)


class MessageSender:
    """Kelas untuk mengirim pesan ke grup."""

    def __init__(
        self,
        client: TelegramClient,
        status_manager: "StatusManager",
    ) -> None:
        """Inisialisasi MessageSender."""
        self.client = client
        self.status = status_manager
        self.batch_size = 4
        self.intra_delay = (2.0, 6.0)
        self.inter_delay = (13.0, 17.0)

    def _create_batches(self, groups: list[str]) -> list[list[str]]:
        """Bagi grup menjadi batch."""
        return [
            groups[i : i + self.batch_size]
            for i in range(0, len(groups), self.batch_size)
        ]

    async def _process_batch(
        self, batch: Sequence[str], message: str
    ) -> tuple[int, int]:
        """Proses satu batch pengiriman."""
        success = 0
        failed = 0
        retry = 0

        for group in batch:
            try:
                if self.status.should_pause_globally():
                    logger.warning("⏳ Pause global karena terlalu banyak FloodWait")
                    failed += len(batch) - (success + failed)
                    break

                await self.client.send_message(group, message)
                success += 1

                if group != batch[-1]:
                    delay = random.uniform(*self.intra_delay)
                    await asyncio.sleep(delay)

            except FloodWaitError:
                if retry >= 3:
                    logger.error("❌ Maksimal retry tercapai")
                    failed += len(batch) - (success + failed)
                    break

                delay = self.status.get_backoff_delay(retry)
                logger.warning("⏳ Retry ke-%d dalam %0.1f detik", retry + 1, delay)
                await asyncio.sleep(delay)
                retry += 1
                continue

            except Exception as e:
                failed += 1
                logger.error("❌ %s: %s", group, str(e))
                continue

        return success, failed

    async def send_messages_in_batches(self, groups: Sequence[str]) -> None:
        """Kirim pesan ke grup dalam batch."""
        if not groups:
            logger.warning("⚠️ Tidak ada grup untuk dikirim")
            return

        batches = self._create_batches(list(groups))
        total_success = 0
        total_failed = 0

        logger.info(
            "📨 Mulai pengiriman ke %d grup (%d batch)",
            len(groups),
            len(batches),
        )

        for i, batch in enumerate(batches, 1):
            try:
                message = self.status.get_random_message()
                logger.info("📨 Batch %d/%d (%d grup)", i, len(batches), len(batch))

                success, failed = await self._process_batch(batch, message)
                total_success += success
                total_failed += failed

                if i < len(batches):
                    delay = random.uniform(*self.inter_delay)
                    logger.info("⏳ Jeda %0.1f detik", delay)
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error("❌ Error batch %d: %s", i, str(e))
                total_failed += len(batch)

        logger.info(
            "✅ Selesai: %d sukses, %d gagal (slowmode: %d, blacklist: %d)",
            total_success,
            total_failed,
            len(self.status._status["slowmode"]),
            len(self.status._status["blacklist"]),
        )
