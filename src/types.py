"""Type hints untuk proyek."""

from typing import Protocol, TypedDict


class SlowmodeInfo(TypedDict):
    """Info slowmode untuk grup.

    Attributes:
        duration: Durasi slowmode dalam detik
        expires_at: UNIX timestamp kapan slowmode berakhir
    """

    duration: float
    expires_at: float


class StatusData(TypedDict):
    """Data status untuk aplikasi.

    Attributes:
        blacklist: Dict grup yang di-blacklist (group: reason)
        slowmode: Dict grup dalam slowmode (group: info)
        last_updated: UNIX timestamp terakhir update
    """

    blacklist: dict[str, str]
    slowmode: dict[str, SlowmodeInfo]
    last_updated: float


class TelegramClientProtocol(Protocol):
    """Protocol untuk client Telegram."""

    async def connect(self) -> None:
        """Connect dan validasi session.

        Raises:
            AuthError: Session string tidak valid
            TelegramError: Error saat connect
        """
        ...

    async def disconnect(self) -> None:
        """Disconnect dari Telegram."""
        ...

    async def send_message(self, chat: str, message: str) -> None:
        """Kirim pesan ke grup.

        Args:
            chat: Username/ID grup
            message: Pesan yang akan dikirim

        Raises:
            TelegramError: Error saat kirim pesan
        """
        ...


class StatusManagerProtocol(Protocol):
    """Protocol untuk status manager."""

    def add_to_blacklist(self, group: str, reason: str) -> None:
        """Tambah grup ke blacklist."""
        ...

    def add_slowmode(self, group: str, duration: float) -> None:
        """Tambah grup ke slowmode."""
        ...

    def get_active_groups(self) -> list[str]:
        """Get list grup aktif."""
        ...

    def cleanup_expired_slowmode(self) -> None:
        """Cleanup slowmode yang sudah expired."""
        ...

    def save(self) -> None:
        """Save status ke file."""
        ...

    def get_groups(self) -> list[str]:
        """Get list grup."""
        ...

    def get_blacklist(self) -> dict[str, str]:
        """Get dict blacklist."""
        ...

    def get_slowmode(self) -> dict[str, SlowmodeInfo]:
        """Get dict slowmode."""
        ...

    def _load_status(self) -> None:
        """Load status dari file."""
        ...


class MessageSenderProtocol(Protocol):
    """Protocol untuk pengirim pesan."""

    async def send_message(self, chat: str, message: str) -> None:
        """Kirim pesan ke grup.

        Args:
            chat: Username/ID grup
            message: Pesan yang akan dikirim

        Raises:
            TelegramError: Error saat kirim pesan
        """
        ...

    async def send_batch(self, groups: list[str]) -> None:
        """Kirim pesan ke batch grup.

        Args:
            groups: List grup yang akan dikirim pesan

        Notes:
            - Template pesan dipilih random
            - Delay 4±2 detik antar pesan
            - Error handling per grup
        """
        ...

    def get_random_template(self) -> str:
        """Get template pesan random.

        Returns:
            Template pesan yang dipilih random

        Raises:
            TelegramError: Tidak ada template pesan
        """
        ...
