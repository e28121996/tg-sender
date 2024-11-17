"""Module untuk mengirim pesan Telegram."""

from pathlib import Path
import random
from typing import Any, Protocol, runtime_checkable

from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    ChatGuestSendForbiddenError,
    ChatRestrictedError,
    ChatWriteForbiddenError,
    FloodWaitError,
    ForbiddenError,
    PeerIdInvalidError,
    SlowModeWaitError,
    UserBannedInChannelError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)

from ..utils.logger import get_logger
from ..utils.status import StatusManager

logger = get_logger(__name__)


@runtime_checkable
class TelegramClientProtocol(Protocol):
    """Protokol untuk client Telegram."""

    async def send_message(self, group_url: str, message: str) -> Any:
        """Mengirim pesan ke grup."""
        ...


class MessageSender:
    """Pengirim pesan ke grup Telegram."""

    def __init__(
        self, client: TelegramClientProtocol, status_manager: StatusManager
    ) -> None:
        """Inisialisasi sender."""
        self.client = client
        self.status_manager = status_manager
        self.templates: list[str] = self._load_templates()
        if not self.templates:
            raise TemplateError()

    @staticmethod
    def _load_templates() -> list[str]:
        """Memuat template pesan dari folder messages."""
        templates: list[str] = []
        messages_dir = Path("data/messages")

        if not messages_dir.exists():
            logger.error("Directory %s tidak ditemukan", messages_dir)
            return templates

        for file in messages_dir.glob("*.txt"):
            try:
                content = file.read_text(encoding="utf-8").strip()
                if content:
                    templates.append(content)
            except Exception as e:
                logger.error("Error membaca %s: %s", file, str(e))

        return templates

    async def send_message(self, group_url: str) -> None:
        """Mengirim pesan ke grup dengan penanganan error sesuai spesifikasi."""
        if not group_url:
            logger.error("URL grup tidak valid")
            return

        try:
            message = random.choice(self.templates)
            await self.client.send_message(group_url, message)
            logger.info("Berhasil mengirim ke %s", group_url)

        except SlowModeWaitError as e:
            wait_seconds = getattr(e, "seconds", 60)
            self.status_manager.add_slowmode(group_url, wait_seconds)
            logger.warning(
                "Slowmode di %s: %ds, melewati grup", group_url, wait_seconds
            )

        except FloodWaitError as e:
            wait_seconds = getattr(e, "seconds", 60)
            logger.error("FloodWait terdeteksi: %ds", wait_seconds)
            raise

        except (
            ChatWriteForbiddenError,
            UserBannedInChannelError,
            ChannelPrivateError,
            ChatAdminRequiredError,
            UsernameInvalidError,
            UsernameNotOccupiedError,
            ChatRestrictedError,
            ChatGuestSendForbiddenError,
            PeerIdInvalidError,
            ForbiddenError,
        ) as e:
            error_msg = e.__class__.__name__
            logger.error("Error blacklist di %s: %s", group_url, error_msg)
            self.status_manager.add_blacklist(group_url, error_msg)

        except Exception as e:
            error_msg = str(e)
            # Tangani error username tidak valid
            if "No user has" in error_msg or "Cannot find any entity" in error_msg:
                error_msg = "UsernameNotOccupiedError"
            logger.error("Error tidak terduga di %s: %s", group_url, error_msg)
            self.status_manager.add_blacklist(group_url, error_msg)


class TemplateError(ValueError):
    """Error untuk template pesan."""

    def __init__(self, message: str = "Template error") -> None:
        super().__init__(message)
