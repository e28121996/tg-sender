"""Type hints untuk proyek."""

from typing import Any, Protocol


# Base types
class SlowmodeInfo(dict):
    """Info slowmode untuk grup."""

    duration: float
    expires_at: float


class StatusData(dict):
    """Data status untuk aplikasi."""

    blacklist: dict[str, str]
    slowmode: dict[str, Any]  # Any untuk hindari circular import
    last_updated: float


# Protocols
class TelegramClientProtocol(Protocol):
    """Protocol untuk client Telegram."""

    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send_message(self, chat: str, message: str) -> None: ...


class StatusManagerProtocol(Protocol):
    """Protocol untuk status manager."""

    def add_to_blacklist(self, group: str, reason: str) -> None: ...
    def add_slowmode(self, group: str, duration: float) -> None: ...
    def get_active_groups(self) -> list[str]: ...
    def cleanup_expired_slowmode(self) -> None: ...
    def save(self) -> None: ...
    def get_groups(self) -> list[str]: ...
    def get_blacklist(self) -> dict[str, str]: ...
    def get_slowmode(self) -> dict[str, Any]: ...


class MessageSenderProtocol(Protocol):
    """Protocol untuk pengirim pesan."""

    async def send_message(self, chat: str, message: str) -> None: ...
    async def send_batch(self, groups: list[str]) -> None: ...
    def get_random_template(self) -> str: ...
