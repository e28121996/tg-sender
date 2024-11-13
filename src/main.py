"""Main entry point untuk aplikasi."""

import asyncio
import random
import sys
from datetime import datetime, timedelta
from typing import Final

from src.bot_runner import BotRunner
from src.config import DATA_DIR, GROUPS_FILE, MESSAGES_DIR
from src.exceptions import AuthError, ConfigError
from src.keep_alive import keep_alive
from src.logger import setup_logger

logger = setup_logger(name=__name__)

# Interval dalam detik (1.1-1.3 jam = 3960-4680 detik)
MIN_INTERVAL: Final[int] = 3960  # 1.1 jam
MAX_INTERVAL: Final[int] = 4680  # 1.3 jam
RETRY_DELAY: Final[int] = 300  # 5 menit


def _raise_config_error(error: str) -> None:
    """Raise config error."""
    raise ConfigError(error)


def validate_environment() -> None:
    """Validasi environment dan struktur folder."""
    try:
        # Validasi folder data
        if not DATA_DIR.exists():
            _raise_config_error(ConfigError.MISSING_DATA_DIR)

        # Validasi file groups.txt
        if not GROUPS_FILE.exists():
            _raise_config_error(ConfigError.MISSING_GROUPS)

        # Validasi folder messages
        if not MESSAGES_DIR.exists() or not MESSAGES_DIR.is_dir():
            _raise_config_error(ConfigError.MISSING_MESSAGES)

        # Validasi template pesan
        message_files = list(MESSAGES_DIR.glob("*.txt"))
        if not message_files:
            _raise_config_error(ConfigError.MISSING_TEMPLATES)

        logger.info("✅ Validasi environment berhasil")

    except Exception:
        logger.exception("❌ Error validasi")
        raise


async def run_scheduled() -> None:
    """Jalankan bot dengan interval."""
    try:
        # Validasi environment dan struktur
        validate_environment()

        # Start web server
        keep_alive()

        # Inisialisasi bot runner
        runner = BotRunner()
        await runner.initialize()

        while True:
            try:
                await runner.run()

                # Generate random interval
                interval: float = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
                next_run: datetime = datetime.now() + timedelta(seconds=interval)

                logger.info(
                    "⏰ Jadwal berikutnya: %s (%.1f jam)",
                    next_run.strftime("%H:%M:%S"),
                    interval / 3600,
                )

                await asyncio.sleep(interval)

            except AuthError:
                logger.exception("❌ Error autentikasi")
                break

            except Exception:
                logger.exception("❌ Error saat jalankan bot")
                logger.info("⏳ Mencoba ulang dalam %d detik", RETRY_DELAY)
                await asyncio.sleep(RETRY_DELAY)

    except Exception:
        logger.exception("❌ Error fatal")
        raise


def main() -> None:
    """Entry point utama."""
    try:
        asyncio.run(run_scheduled())
    except KeyboardInterrupt:
        logger.info("👋 Bot dihentikan oleh user")
    except Exception:
        logger.exception("❌ Error fatal")
        sys.exit(1)


if __name__ == "__main__":
    main()
