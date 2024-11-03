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


def validate_environment() -> None:
    """Validasi environment dan struktur folder."""
    try:
        # Validasi folder data
        if not DATA_DIR.exists():
            raise ConfigError("Folder data/ tidak ditemukan")

        # Validasi file groups.txt
        if not GROUPS_FILE.exists():
            raise ConfigError("File groups.txt tidak ditemukan")

        # Validasi folder messages
        if not MESSAGES_DIR.exists() or not MESSAGES_DIR.is_dir():
            raise ConfigError("Folder messages/ tidak ditemukan")

        # Validasi template pesan
        message_files = list(MESSAGES_DIR.glob("*.txt"))
        if not message_files:
            raise ConfigError("Tidak ada template pesan di folder messages/")

        logger.info("✅ Validasi environment berhasil")

    except Exception as e:
        logger.error("❌ Error validasi: %s", str(e))
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

            except AuthError as e:
                logger.error("❌ Error autentikasi: %s", str(e))
                break

            except Exception as e:
                logger.error("❌ Error saat jalankan bot: %s", str(e))
                logger.info("⏳ Mencoba ulang dalam %d detik", RETRY_DELAY)
                await asyncio.sleep(RETRY_DELAY)

    except Exception as e:
        logger.error("❌ Error fatal: %s", str(e))
        raise


def main() -> None:
    """Entry point utama."""
    try:
        asyncio.run(run_scheduled())
    except KeyboardInterrupt:
        logger.info("👋 Bot dihentikan oleh user")
    except Exception as e:
        logger.error("❌ Error fatal: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
