"""Modul untuk menangani operasi pengiriman pesan."""

import asyncio
import random
import time
from typing import List

from .config import CONFIG
from .error_handler import ErrorHandler
from .logger import setup_logger
from .status_manager import StatusManager
from .telegram_client import TelegramSenderClient

logger = setup_logger(__name__, CONFIG.logging["file"])


class MessageSender:
    """Menangani pengiriman pesan ke grup Telegram."""

    def __init__(
        self,
        telegram_client: TelegramSenderClient,
        status_manager: StatusManager,
        error_handler: ErrorHandler,
    ) -> None:
        """
        Inisialisasi MessageSender.

        Args:
            telegram_client: Klien Telegram untuk mengirim pesan.
            status_manager: Pengelola status grup.
            error_handler: Penangan kesalahan.
        """
        self.telegram_client = telegram_client
        self.status_manager = status_manager
        self.error_handler = error_handler
        self.messages = self._load_messages()
        logger.info("MessageSender diinisialisasi")

    def _load_messages(self) -> List[str]:
        """Muat template pesan dari file."""
        messages = []
        for filename in CONFIG.message_files:
            with open(filename, "r") as f:
                messages.append(f.read().strip())
        logger.info(f"Berhasil memuat {len(messages)} template pesan")
        return messages

    async def send_messages(self, groups: List[str]) -> None:
        """Kirim pesan ke semua grup yang diberikan."""
        start_time = time.time()
        logger.info(f"Memulai sesi pengiriman pesan ke {len(groups)} grup")
        filtered_groups = self._filter_groups(groups)
        logger.info(f"Jumlah grup yang akan dicoba: {len(filtered_groups)}")

        batches = self._create_batches(filtered_groups, CONFIG.messaging["batch_size"])
        for i, batch in enumerate(batches, 1):
            logger.info(f"Memulai pengiriman batch ke-{i} dari {len(batches)}")
            await self._send_batch(batch)
            if i < len(batches):
                delay = random.uniform(
                    CONFIG.messaging["inter_batch_delay"]["min"],
                    CONFIG.messaging["inter_batch_delay"]["max"],
                )
                logger.info(f"Menunggu {delay:.2f} detik sebelum batch berikutnya")
                await asyncio.sleep(delay)

        self.status_manager.save_status()
        self.status_manager.log_metrics()
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(
            f"Sesi pengiriman pesan selesai. Total grup dicoba: {len(filtered_groups)}. "
            f"Waktu total: {total_time:.2f} detik"
        )

    def _filter_groups(self, groups: List[str]) -> List[str]:
        return [
            group
            for group in groups
            if not self.status_manager.is_blacklisted(group)
            and not self.status_manager.is_in_slowmode(group)
        ]

    async def _send_batch(self, batch: List[str]) -> None:
        """Kirim pesan ke batch grup."""
        for group in batch:
            if self.status_manager.is_blacklisted(group):
                logger.info(f"Melewati grup {group} (dalam blacklist)")
                continue
            if self.status_manager.is_in_slowmode(group):
                logger.info(f"Melewati grup {group} (dalam slowmode)")
                continue

            try:
                message = random.choice(self.messages)
                logger.info(f"Mencoba mengirim pesan ke {group}")
                await self.error_handler.retry_with_backoff(
                    self.telegram_client.send_message, group, message
                )
                logger.info(f"Pesan berhasil dikirim ke {group}")
                self.status_manager.messages_sent += 1
            except Exception as e:
                logger.error(f"Gagal mengirim pesan ke {group}: {e}")
                self.status_manager.messages_failed += 1
                await self.error_handler.handle_error(e, group)
                continue

            delay = random.uniform(
                CONFIG.messaging["intra_batch_delay"]["min"],
                CONFIG.messaging["intra_batch_delay"]["max"],
            )
            logger.info(f"Menunggu {delay:.2f} detik sebelum pesan berikutnya")
            await asyncio.sleep(delay)

    @staticmethod
    def _create_batches(items: List[str], batch_size: int) -> List[List[str]]:
        """Buat batch dari daftar item."""
        return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
