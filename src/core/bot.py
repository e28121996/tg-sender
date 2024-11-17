import asyncio
from pathlib import Path
import random
import time
from typing import ClassVar

from telethon.errors import FloodWaitError

from ..utils.logger import get_logger
from ..utils.status import StatusManager
from .client import TelegramClient
from .sender import MessageSender

logger = get_logger(__name__)


class StructureError(ValueError):
    """Error untuk struktur folder/file yang tidak valid."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Required path {path} not found")


class TemplateNotFoundError(ValueError):
    """Error ketika tidak ada template pesan."""

    def __init__(self) -> None:
        super().__init__("No message templates found")


class BotRunner:
    """Bot untuk mengirim pesan ke grup Telegram secara otomatis."""

    BATCH_SIZE: ClassVar[int] = 4
    BATCH_INTERVAL: ClassVar[int] = 15
    MESSAGE_INTERVAL: ClassVar[int] = 5

    def __init__(self) -> None:
        self.status_manager = StatusManager()
        self.client = TelegramClient()
        self.sender = MessageSender(self.client, self.status_manager)
        self._running = True
        self._shutdown_event = asyncio.Event()

    @staticmethod
    def _validate_structure() -> None:
        """Validasi struktur folder dan file yang dibutuhkan."""
        required_paths = [
            Path("data"),
            Path("data/messages"),
            Path("data/groups.txt"),
        ]

        for path in required_paths:
            if not path.exists():
                logger.error("Struktur tidak valid: %s tidak ditemukan", path)
                raise StructureError(str(path))

        if not list(Path("data/messages").glob("*.txt")):
            logger.error("Tidak ada template pesan di data/messages/")
            raise TemplateNotFoundError()

    async def _wait_next_session(self) -> None:
        """Menunggu interval sebelum sesi berikutnya."""
        if not self._running:
            return
        interval = random.uniform(1.1, 1.3) * 3600  # 1.1-1.3 jam
        logger.info("Menunggu %.2f jam untuk sesi berikutnya", interval / 3600)
        await asyncio.sleep(interval)

    async def start(self) -> None:
        """Memulai bot dan proses pengiriman."""
        try:
            # Validasi struktur di awal
            self._validate_structure()

            if not self._running:
                return

            await self.client.start()

            while self._running:
                try:
                    await self.run_session()
                except FloodWaitError as e:
                    wait_seconds = getattr(e, "seconds", 60)
                    logger.warning(
                        "Sesi dihentikan karena FloodWait: %ds", wait_seconds
                    )
                    if self._running:
                        await asyncio.sleep(wait_seconds)
                        await self._wait_next_session()
                except Exception as e:
                    logger.error("Error dalam sesi: %s", str(e))
                    if self._running:
                        await self._wait_next_session()

                if self._shutdown_event.is_set():
                    break

        except Exception as e:
            logger.error("Error fatal dalam bot: %s", str(e))
        finally:
            await self.shutdown()

    async def stop(self) -> None:
        """Menghentikan bot dengan aman."""
        if not self._running:
            return
        self._running = False
        self._shutdown_event.set()
        await self.shutdown()

    def _log_statistics(self, active_groups: list[str]) -> None:
        """Mencatat statistik detail tentang grup."""
        try:
            all_groups = self.status_manager.get_all_groups()
            blacklist = self.status_manager.status["blacklist"]
            slowmode = self.status_manager.status["slowmode"]

            # Statistik umum
            logger.info(
                "Statistik Grup - Total: %d, Blacklist: %d, Slowmode: %d, Aktif: %d",
                len(all_groups),
                len(blacklist),
                len(slowmode),
                len(active_groups),
            )

            # Detail blacklist per kategori error
            error_categories: dict[str, int] = {}
            for reason in blacklist.values():
                error_categories[reason] = error_categories.get(reason, 0) + 1

            if error_categories:
                logger.info("Distribusi Error Blacklist:")
                for error_type, count in error_categories.items():
                    logger.info("  - %s: %d grup", error_type, count)

            # Info slowmode
            if slowmode:
                current_time = time.time()
                active_slowmodes = [
                    (url, expire_time)
                    for url, expire_time in slowmode.items()
                    if expire_time > current_time
                ]

                if active_slowmodes:
                    logger.info("Status Slowmode Aktif:")
                    for url, expire_time in active_slowmodes:
                        remaining = int(expire_time - current_time)
                        logger.info("  - %s: %d detik tersisa", url, remaining)

        except Exception as e:
            logger.error("Error saat logging statistik: %s", str(e))

    async def run_session(self) -> None:
        """Menjalankan satu sesi pengiriman."""
        # Pre-send: Bersihkan slowmode kadaluarsa
        self.status_manager.clean_expired_slowmode()

        # Dapatkan grup aktif dan log statistik
        active_groups = self.status_manager.get_active_groups()
        self._log_statistics(active_groups)

        if not active_groups:
            logger.info("Tidak ada grup aktif, menunggu sesi berikutnya...")
            await self._wait_next_session()
            return

        batches = self._create_batches(active_groups)
        logger.info(
            "Memulai sesi dengan %d grup dalam %d batch",
            len(active_groups),
            len(batches),
        )

        try:
            for batch in batches:
                if not self._running or self._shutdown_event.is_set():
                    break
                await self.process_batch(batch)
                await asyncio.sleep(self.BATCH_INTERVAL)

            # Log statistik akhir
            logger.info("Sesi selesai, mencatat statistik akhir")
            self._log_statistics(self.status_manager.get_active_groups())

        except Exception as e:
            logger.error("Error dalam batch: %s", str(e))
        finally:
            # Pastikan selalu menunggu interval sebelum sesi berikutnya
            if self._running and not self._shutdown_event.is_set():
                await self._wait_next_session()

    async def process_batch(self, batch: list[str]) -> None:
        """Memproses satu batch grup."""
        logger.info("Memproses batch dengan %d grup", len(batch))
        for group in batch:
            if not self._running:
                break
            await self.sender.send_message(group)
            await asyncio.sleep(self.MESSAGE_INTERVAL)

    async def shutdown(self) -> None:
        """Membersihkan resources saat shutdown."""
        if hasattr(self, "_shutdown_complete"):
            return

        self._running = False
        self._shutdown_event.set()
        try:
            await self.client.disconnect()
            logger.info("Client berhasil disconnect")
        except Exception as e:
            logger.error("Error saat shutdown: %s", str(e))
        finally:
            self.status_manager.save()
            self._shutdown_complete = True
            logger.info("Shutdown selesai")

    @staticmethod
    def _create_batches(items: list[str]) -> list[list[str]]:
        """Membagi list menjadi batch dengan ukuran tertentu."""
        return [
            items[i : i + BotRunner.BATCH_SIZE]
            for i in range(0, len(items), BotRunner.BATCH_SIZE)
        ]
