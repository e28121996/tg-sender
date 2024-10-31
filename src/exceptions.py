"""Modul untuk exception kustom."""


class TelegramError(Exception):
    """Base exception untuk error Telegram."""

    def __init__(self, message: str) -> None:
        """Inisialisasi exception dengan pesan."""
        self.message = message
        super().__init__(self.message)


class AuthError(TelegramError):
    """Exception untuk error autentikasi."""

    def __init__(self, message: str = "Autentikasi gagal") -> None:
        """Inisialisasi AuthError."""
        super().__init__(message)


class ConfigError(TelegramError):
    """Exception untuk error konfigurasi."""

    def __init__(self, message: str = "Konfigurasi tidak lengkap") -> None:
        """Inisialisasi ConfigError."""
        super().__init__(message)


class StatusError(TelegramError):
    """Exception untuk error status."""

    def __init__(self, message: str) -> None:
        """Inisialisasi StatusError."""
        super().__init__(message)


class SlowModeError(TelegramError):
    """Exception untuk error slowmode."""

    def __init__(self, duration: int) -> None:
        """Inisialisasi SlowModeError dengan durasi."""
        super().__init__(f"Slowmode {duration} detik")
        self.duration = duration


class FloodWaitError(TelegramError):
    """Exception untuk error FloodWait."""

    def __init__(self, seconds: int) -> None:
        """Inisialisasi FloodWaitError dengan waktu tunggu."""
        super().__init__(f"FloodWait {seconds} detik")
        self.seconds = seconds
