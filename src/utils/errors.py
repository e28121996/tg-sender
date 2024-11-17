class TelegramError(Exception):
    """Base class untuk semua error telegram."""


class AuthError(TelegramError):
    """Client tidak terautentikasi."""


class ClientError(TelegramError):
    """Client belum dimulai atau error."""


class DisconnectError(TelegramError):
    """Gagal memutuskan koneksi client."""


class TemplateError(TelegramError):
    """Template pesan tidak tersedia."""
