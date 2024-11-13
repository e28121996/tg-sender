"""Modul untuk exception handling."""


class TelegramError(Exception):
    """Base class untuk error Telegram."""

    PREFIX = "[TG] "
    TIMEOUT_MSG = "Timeout setelah {} detik"
    UNEXPECTED_MSG = "Error tidak terduga"

    # Error messages
    CLIENT_UNINITIALIZED = "Client belum diinisialisasi"
    CONNECT_TIMEOUT = "Timeout saat connect: {} detik"
    CONNECT_ERROR = "Error saat connect: {}"
    SEND_TIMEOUT = "Timeout setelah {} detik"
    SEND_ERROR = "Error saat kirim pesan: {}"
    GROUP_ACCESS_DENIED = "Tidak memiliki akses ke grup"
    USERNAME_INVALID = "Username tidak valid: {}"
    GROUP_BANNED = "Akun diblokir dari grup: {}"
    GROUP_PRIVATE = "Grup bersifat private: {}"
    PERMISSION_DENIED = "Tidak memiliki izin di grup: {}"
    LINK_INVALID = "Format link tidak valid: {}"
    INVALID_FOLDER = "Folder template tidak valid: {}"
    NO_TEMPLATES = "Tidak ada template pesan"
    EMPTY_TEMPLATES = "Semua template pesan kosong"
    LOAD_TEMPLATE_ERROR = "Error saat load template: {}"

    def __init__(self, message: str) -> None:
        """Initialize dengan format pesan yang konsisten."""
        super().__init__(f"{self.PREFIX}{message}")

    @classmethod
    def timeout(cls, seconds: int) -> "TelegramError":
        """Create timeout error."""
        return cls(cls.TIMEOUT_MSG.format(seconds))

    @classmethod
    def unexpected(cls) -> "TelegramError":
        """Create unexpected error."""
        return cls(cls.UNEXPECTED_MSG)

    @classmethod
    def connect_timeout(cls, seconds: int) -> "TelegramError":
        """Create connect timeout error."""
        return cls(cls.CONNECT_TIMEOUT.format(seconds))

    @classmethod
    def connect_error(cls, error: str) -> "TelegramError":
        """Create connect error."""
        return cls(cls.CONNECT_ERROR.format(error))


class AuthError(Exception):
    """Error untuk autentikasi."""

    SESSION_INVALID = "Session string tidak valid"
    AUTH_FAILED = "Gagal autentikasi: {}"


class SlowModeError(Exception):
    """Error untuk slowmode."""

    def __init__(self, seconds: int) -> None:
        """Initialize dengan durasi slowmode."""
        super().__init__(f"Slowmode aktif, tunggu {seconds} detik")
        self.seconds = seconds


class StatusError(Exception):
    """Error untuk status manager."""

    INVALID_FORMAT = "Format status tidak valid: {}"
    MISSING_GROUPS = "File groups.txt tidak ditemukan"
    LOAD_GROUPS_ERROR = "Error saat load groups: {}"
    SAVE_ERROR = "Error saat save status: {}"
    INVALID_BLACKLIST = "Format blacklist tidak valid"
    INVALID_BLACKLIST_DATA = "Data blacklist tidak valid"
    INVALID_SLOWMODE = "Format slowmode tidak valid"
    INVALID_SLOWMODE_DATA = "Data slowmode tidak valid"


class ConfigError(Exception):
    """Error untuk konfigurasi."""

    MISSING_ENV = "Environment variable {} tidak ditemukan. Set di Replit Secrets tab"
    MISSING_DATA_DIR = "Folder data tidak ditemukan"
    MISSING_GROUPS = "File groups.txt tidak ditemukan"
    MISSING_MESSAGES = "Folder messages tidak ditemukan"
    MISSING_TEMPLATES = "Tidak ada template pesan di folder messages"
    LOAD_ERROR = "Error saat load config: {}"
    INVALID_API_ID = "API_ID harus berupa angka"

    def __init__(self, message: str) -> None:
        """Initialize dengan format pesan yang konsisten."""
        if message.startswith("MISSING_ENV:"):
            # Format pesan untuk missing env vars
            vars = message.split(":")[1]
            message = self.MISSING_ENV.format(vars)
        elif message == "INVALID_API_ID":
            message = self.INVALID_API_ID
        super().__init__(message)
