"""Custom exceptions untuk aplikasi."""

from typing import Final

# Error codes
ERR_CONFIG: Final[str] = "CFG"  # Configuration/environment errors
ERR_AUTH: Final[str] = "AUTH"  # Authentication errors
ERR_TELEGRAM: Final[str] = "TG"  # Telegram API errors
ERR_STATUS: Final[str] = "STS"  # Status management errors


class BotError(Exception):
    """Base exception untuk semua error bot.

    Attributes:
        code: Kode error untuk identifikasi
        message: Pesan error yang deskriptif
    """

    def __init__(self, message: str, code: str = "") -> None:
        """Initialize exception.

        Args:
            message: Pesan error yang deskriptif
            code: Kode error untuk identifikasi
        """
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}" if code else message)


class ConfigError(BotError):
    """Error konfigurasi atau environment.

    Digunakan untuk:
    - Environment variables tidak lengkap/invalid
    - File konfigurasi tidak valid/missing
    - Struktur folder/file tidak sesuai
    - Bot belum diinisialisasi
    """

    def __init__(self, message: str) -> None:
        """Initialize config error."""
        super().__init__(message, ERR_CONFIG)


class AuthError(BotError):
    """Error autentikasi Telegram.

    Digunakan untuk:
    - Session string tidak valid/expired
    - API credentials salah/invalid
    - Akun dibanned/restricted
    - User tidak terautentikasi
    """

    def __init__(self, message: str) -> None:
        """Initialize auth error."""
        super().__init__(message, ERR_AUTH)


class TelegramError(BotError):
    """Error operasi Telegram.

    Digunakan untuk:
    - Network error/timeout
    - Rate limiting/flood wait
    - API error responses
    - Slowmode restrictions
    - Permission errors
    - Invalid group/chat errors
    """

    def __init__(self, message: str) -> None:
        """Initialize telegram error."""
        super().__init__(message, ERR_TELEGRAM)


class StatusError(BotError):
    """Error manajemen status.

    Digunakan untuk:
    - File status.json corrupt/invalid
    - Error saat save/load status
    - Struktur data tidak valid
    - Validasi data gagal
    """

    def __init__(self, message: str) -> None:
        """Initialize status error."""
        super().__init__(message, ERR_STATUS)


class SlowModeError(TelegramError):
    """Error untuk slowmode."""

    def __init__(self, seconds: float) -> None:
        """Init dengan durasi slowmode."""
        super().__init__(f"Slowmode wait: {seconds} seconds")
        self.seconds = seconds
