"""Modul untuk menjalankan bot."""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import Final

from .exceptions import SlowModeError
from .logger import (
    DELAY_EMOJI,
    ERROR_EMOJI,
    SAVE_EMOJI,
    STATS_EMOJI,
    WARNING_EMOJI,
    setup_logger,
)
from .message_sender import MessageSender
from .status_manager import StatusManager
from .telegram_client import TelegramClient

logger = setup_logger(name=__name__)

# Konstanta untuk pengiriman pesan
BATCH_SIZE: Final[int] = 4  # Jumlah pesan per batch
BATCH_DELAY: Final[tuple[int, int]] = (13, 17)  # Interval delay antar batch
MIN_INTERVAL: Final[int] = 3960  # 1.1 jam
MAX_INTERVAL: Final[int] = 4680  # 1.3 jam


class BotRunner:
    """Class untuk menjalankan bot."""

    def __init__(self) -> None:
        """Initialize bot runner."""
        self.status = StatusManager()
        self.client = TelegramClient(self.status)
        self.sender = MessageSender(self.client, self.status)

    def _create_batches(
        self, items: list[str], size: int = BATCH_SIZE
    ) -> list[list[str]]:
        """Create batches dari list."""
        return [items[i : i + size] for i in range(0, len(items), size)]

    def _get_next_run_time(self) -> datetime:
        """Get waktu untuk run berikutnya."""
        delay = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
        return datetime.now() + timedelta(seconds=delay)

    def _format_duration(self, next_run: datetime) -> str:
        """Format durasi ke string."""
        delta = next_run - datetime.now()
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{hours}.{minutes:02d} jam"

    async def initialize(self) -> None:
        """Inisialisasi bot runner."""
        try:
            await self.client.connect()
            logger.info("✅ Bot berhasil diinisialisasi")
        except Exception:
            logger.exception("Error saat inisialisasi bot")
            await self.client.disconnect()
            raise

    async def run(self) -> None:
        """Jalankan bot."""
        try:
            # 1. Pre-run cleanup
            self.status.cleanup_status()  # Hanya cleanup slowmode
            self._log_statistics()

            # 2. Get dan validasi active groups
            active_groups = list(self.status.get_active_groups())
            if not active_groups:
                logger.warning(f"{WARNING_EMOJI} Tidak ada grup aktif!")
                return

            # 3. Log total batch yang akan diproses
            total_batches = (len(active_groups) + BATCH_SIZE - 1) // BATCH_SIZE
            logger.info(
                f"📦 Memulai pengiriman: {len(active_groups)} grup dalam {total_batches} batch"
            )

            # Track statistik global
            global_stats = {
                "success": 0,
                "failed": 0,
                "blacklisted": 0,
                "slowmode": 0,
                "start_time": time.time(),
                "total_groups": len(active_groups),
            }

            # 4. Batch processing
            batches = self._create_batches(active_groups)
            for i, batch in enumerate(batches, 1):
                try:
                    batch_stats = await self.sender.send_batch(batch, i, total_batches)
                    # Update statistik global
                    if batch_stats:
                        for key in ["success", "failed", "blacklisted", "slowmode"]:
                            global_stats[key] += batch_stats.get(key, 0)

                    # Cleanup slowmode setelah setiap batch
                    self.status.cleanup_expired_slowmode()

                except SlowModeError:
                    logger.info("💡 Menunggu slowmode selesai...")
                    global_stats["slowmode"] += 1
                    continue
                except Exception:
                    logger.exception(f"{ERROR_EMOJI} Error pada batch {i}")
                    continue

                # Delay antar batch jika masih ada batch berikutnya
                if i < total_batches:
                    delay = random.uniform(*BATCH_DELAY)
                    logger.info(f"{DELAY_EMOJI} Delay {delay:.1f}s ke batch berikutnya")
                    await asyncio.sleep(delay)

            # 5. Final cleanup dan log statistik akhir
            self.status.cleanup_expired_slowmode()  # Cleanup final
            duration = time.time() - global_stats["start_time"]
            total = global_stats["total_groups"]
            if total > 0:
                logger.info(
                    f"📊 Hasil: {duration:.1f}s | "
                    f"Total: {total} | "
                    f"✅ {global_stats['success']}/{total} | "
                    f"❌ {global_stats['failed']} | "
                    f"⏳ {len(self.status.get_slowmode())} | "
                    f"Rata-rata: {duration/total:.1f}s"
                )

            # 6. Post-run cleanup dan jadwal berikutnya
            self.status.save()
            logger.info(f"{SAVE_EMOJI} Status tersimpan")

        except Exception:
            logger.exception(f"{ERROR_EMOJI} Error fatal")
            raise

        finally:
            await self.client.disconnect()

    def _log_statistics(self) -> None:
        """Log statistik detail."""
        total = len(self.status.get_groups())
        active = len(self.status.get_active_groups())
        blacklist = len(self.status.get_blacklist())
        slowmode = len(self.status.get_slowmode())

        logger.info(
            f"{STATS_EMOJI} Status: {total} grup | "
            f"✅ {active} aktif | "
            f"⛔ {blacklist} blacklist | "
            f"⏳ {slowmode} slowmode"
        )
