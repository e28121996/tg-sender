"""Type hints untuk proyek."""

from typing import Any, Protocol, TypedDict


# Base types
class SlowmodeInfo(dict[str, float]):
    """Info slowmode untuk grup."""

    duration: float
    expires_at: float


class StatusData(dict[str, Any]):
    """Data status untuk aplikasi."""

    blacklist: dict[str, str]
    slowmode: dict[str, Any]  # Any untuk hindari circular import
    last_updated: float


# Protocols
class TelegramClientProtocol(Protocol):
    """Protocol untuk client Telegram."""

    async def connect(self) -> None:
        """Connect ke Telegram."""
        ...

    async def disconnect(self) -> None:
        """Disconnect dari Telegram."""
        ...

    async def send_message(self, chat: str, message: str) -> None:
        """Kirim pesan ke grup."""
        ...

    def _validate_client(self) -> Any:
        """Validasi client sudah diinisialisasi."""
        ...


class StatusManagerProtocol(Protocol):
    """Protocol untuk status manager."""

    def add_to_blacklist(self, group: str, reason: str) -> None:
        """Tambah grup ke blacklist."""
        ...

    def add_slowmode(self, group: str, duration: float) -> None:
        """Tambah grup ke slowmode."""
        ...

    def get_active_groups(self) -> set[str]:
        """Get list grup aktif."""
        ...

    def cleanup_expired_slowmode(self) -> None:
        """Cleanup slowmode yang expired."""
        ...

    def save(self) -> None:
        """Save status ke file."""
        ...

    def get_groups(self) -> set[str]:
        """Get list grup."""
        ...

    def get_blacklist(self) -> dict[str, str]:
        """Get dict blacklist."""
        ...

    def get_slowmode(self) -> dict[str, Any]:
        """Get dict slowmode."""
        ...

    def cleanup_status(self) -> None:
        """Cleanup status yang tidak valid."""
        ...

    def get_slowmode_info(self, group: str) -> dict[str, float] | None:
        """Get informasi slowmode untuk grup."""
        ...


BatchStats = dict[str, int | float]


class MessageSenderProtocol(Protocol):
    """Protocol untuk pengirim pesan."""

    async def send_message(self, chat: str, message: str) -> None:
        """Kirim pesan ke grup."""
        ...

    async def send_batch(
        self, groups: list[str], current_batch: int = 1, total_batches: int = 1
    ) -> BatchStats:
        """Kirim pesan ke batch grup."""
        ...

    def get_random_template(self) -> str:
        """Get template pesan random."""
        ...


class InvalidGroups(TypedDict):
    """Type untuk grup yang tidak valid."""

    format: list[str]  # Format tidak valid
    blacklist: dict[str, str]  # Grup yang di-blacklist dengan alasannya
