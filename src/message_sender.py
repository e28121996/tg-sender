"""Modul untuk mengirim pesan ke grup."""

import asyncio
import random
import time
from typing import Final

from .config import MESSAGES_DIR
from .custom_types import BatchStats, MessageSenderProtocol
from .exceptions import TelegramError
from .logger import setup_logger
from .status_manager import StatusManager
from .telegram_client import TelegramClient

logger = setup_logger(name=__name__)

# Konstanta untuk pengiriman pesan
BATCH_SIZE: Final[int] = 4  # Jumlah pesan per batch
MESSAGE_DELAY: Final[tuple[int, int]] = (2, 6)  # Interval 4±2 detik

# Emoji untuk status
SUCCESS_EMOJI: Final[str] = "✅"
ERROR_EMOJI: Final[str] = "❌"
DELAY_EMOJI: Final[str] = "⏳"
STATS_EMOJI: Final[str] = "📊"


def _raise_template_error(error: str) -> None:
    """Raise template error."""
    raise TelegramError(error) from None


class MessageSender(MessageSenderProtocol):
    """Class untuk mengirim pesan ke grup."""

    def __init__(self, client: TelegramClient, status: StatusManager) -> None:
        """Initialize message sender."""
        self.client = client
        self.status = status
        self._templates: list[str] = []
        self._load_templates()

    def _load_templates(self) -> None:
        """Load template pesan dari folder messages/."""
        try:
            message_files = list(MESSAGES_DIR.glob("*.txt"))
            if not message_files:
                _raise_template_error(TelegramError.NO_TEMPLATES)

            for file in message_files:
                content = file.read_text().strip()
                if content:
                    self._templates.append(content)

            if not self._templates:
                _raise_template_error(TelegramError.EMPTY_TEMPLATES)

            logger.info("✅ Berhasil load %d template pesan", len(self._templates))

        except Exception as e:
            logger.exception("Error saat load template")
            raise TelegramError(TelegramError.LOAD_TEMPLATE_ERROR.format(str(e))) from e

    def get_random_template(self) -> str:
        """Get template pesan random."""
        if not self._templates:
            _raise_template_error(TelegramError.NO_TEMPLATES)
        return random.choice(self._templates)

    async def send_batch(
        self, groups: list[str], current_batch: int = 1, total_batches: int = 1
    ) -> BatchStats:
        """Kirim pesan ke batch grup."""
        if not groups:
            return {
                "success": 0,
                "failed": 0,
                "slowmode": 0,
                "start_time": time.time(),
            }

        stats: BatchStats = {
            "success": 0,
            "failed": 0,
            "slowmode": 0,
            "start_time": time.time(),
        }

        active_groups = [g for g in groups if g not in self.status.get_blacklist()]
        if not active_groups:
            return stats

        logger.info(
            f"📦 Batch {current_batch}/{total_batches} ({len(active_groups)} grup)"
        )

        template = self.get_random_template()
        for group in active_groups:
            try:
                if self.status.is_slowmode_active(group):
                    stats["slowmode"] += 1
                    slowmode_info = self.status.get_slowmode_info(group)
                    if slowmode_info:
                        logger.warning(
                            f"{DELAY_EMOJI} {group} - Slowmode "
                            f"{slowmode_info.get('duration', 0)}s"
                        )
                    continue

                await self.client.send_message(group, template)
                stats["success"] += 1
                logger.info(f"{SUCCESS_EMOJI} {group}")

            except TelegramError:
                stats["failed"] += 1

            except Exception:
                stats["failed"] += 1
                logger.warning(f"{ERROR_EMOJI} {group} - Error tidak terduga")

            if group != active_groups[-1]:
                await asyncio.sleep(random.uniform(*MESSAGE_DELAY))

        # Log ringkasan batch dalam satu baris
        duration = time.time() - stats["start_time"]
        total = len(active_groups)
        if total > 0:
            logger.info(
                f"📊 Batch {current_batch}/{total_batches}: {duration:.1f}s | "
                f"✅ {stats['success']}/{total} | "
                f"❌ {stats['failed']} | "
                f"⏳ {stats['slowmode']}"
            )

        return stats

    async def send_message(self, chat: str, message: str) -> None:
        """Kirim pesan ke grup."""
        await self.client.send_message(chat, message)
