"""Modul utilitas untuk fungsi-fungsi pembantu."""

import asyncio
import os
from typing import Any, Callable

from .config import CONFIG
from .logger import setup_logger

logger = setup_logger(__name__, CONFIG.logging["file"])

PID_FILE = "bot.pid"


def create_pid_file() -> bool:
    """Buat file PID jika belum ada."""
    if os.path.exists(PID_FILE):
        logger.warning(f"File PID {PID_FILE} sudah ada, bot mungkin sudah berjalan")
        return False
    with open(PID_FILE, "w") as f:
        pid = os.getpid()
        f.write(str(pid))
    logger.info(f"File PID {PID_FILE} berhasil dibuat dengan PID {pid}")
    return True


def remove_pid_file() -> None:
    """Hapus file PID jika ada."""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
        logger.info(f"File PID {PID_FILE} berhasil dihapus")


async def retry_with_backoff(
    func: Callable[..., Any],
    max_attempts: int,
    initial_delay: float,
    backoff_factor: float,
    *args: Any,
    **kwargs: Any,
) -> Any:
    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.error(f"Gagal setelah {max_attempts} percobaan: {e}")
                raise
            delay = initial_delay * (backoff_factor**attempt)
            logger.warning(
                f"Percobaan {attempt + 1} gagal. Mencoba lagi dalam {delay:.2f} detik"
            )
            await asyncio.sleep(delay)
