"""Modul untuk setup logging."""

import logging
import sys
from types import TracebackType
from typing import Final

# Konstanta logging
LOG_FORMAT: Final[str] = "%(asctime)s - %(levelname)s - %(message)s"  # Hapus nama modul
DATE_FORMAT: Final[str] = "%H:%M:%S"  # Format waktu lebih ringkas
LOG_LEVEL: Final[int] = logging.INFO

# Emoji untuk status
SUCCESS_EMOJI: Final[str] = "🟢"  # Sukses/berhasil
ERROR_EMOJI: Final[str] = "🔴"  # Error/gagal
WARNING_EMOJI: Final[str] = "🟡"  # Warning/peringatan
INFO_EMOJI: Final[str] = "💡"  # Info umum
BATCH_EMOJI: Final[str] = "📦"  # Batch pengiriman
STATS_EMOJI: Final[str] = "📊"  # Statistik/ringkasan
DELAY_EMOJI: Final[str] = "⏳"  # Delay/tunggu
INIT_EMOJI: Final[str] = "🚀"  # Inisialisasi/startup
EXIT_EMOJI: Final[str] = "👋"  # Exit/shutdown
BLACKLIST_EMOJI: Final[str] = "⛔"  # Blacklist
SLOWMODE_EMOJI: Final[str] = "🕒"  # Slowmode
SEND_EMOJI: Final[str] = "📨"  # Pengiriman pesan
RETRY_EMOJI: Final[str] = "🔄"  # Retry/ulang
CONFIG_EMOJI: Final[str] = "🔧"  # Konfigurasi
VALIDATE_EMOJI: Final[str] = "✅"  # Validasi
CLEANUP_EMOJI: Final[str] = "🧹"  # Untuk cleanup
SAVE_EMOJI: Final[str] = "💾"  # Untuk save
UPDATE_EMOJI: Final[str] = "🔄"  # Untuk update


# Type untuk exception info
ExcInfo = (
    tuple[type[BaseException], BaseException, TracebackType | None]
    | tuple[None, None, None]
)


class CompactExceptionFormatter(logging.Formatter):
    """Format exception tanpa traceback."""

    def format_exception(self, ei: ExcInfo) -> str:
        """Format exception message saja."""
        if ei[1] is not None:
            return f"{ei[1]}"
        return ""


def setup_logger(name: str) -> logging.Logger:
    """Setup logger dengan format standar."""
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    if logger.handlers:
        _loggers[name] = logger
        return logger

    formatter = CompactExceptionFormatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    logger.propagate = False

    _loggers[name] = logger
    return logger


# Cache untuk logger yang sudah dibuat
_loggers: dict[str, logging.Logger] = {}
