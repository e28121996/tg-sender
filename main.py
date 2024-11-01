"""Main entry point untuk aplikasi."""

import asyncio
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Final

from keep_alive import keep_alive
from src.bot_runner import BotRunner
from src.exceptions import AuthError, ConfigError, TelegramError
from src.logger import setup_logger

logger = setup_logger(name="telegram_sender")

# Interval dalam detik (1.1-1.3 jam = 3960-4680 detik)
MIN_INTERVAL: Final[int] = 3960  # 1.1 jam
MAX_INTERVAL: Final[int] = 4680  # 1.3 jam


def validate_environment() -> None:
    """Validasi environment dan struktur folder."""
    required = ["API_ID", "API_HASH", "PHONE_NUMBER", "SESSION_STRING"]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        logger.error("❌ Environment variables tidak lengkap: %s", ", ".join(missing))
        sys.exit(1)

    data_dir = Path("data")
    if not data_dir.exists():
        logger.error("❌ Folder data/ tidak ditemukan")
        sys.exit(1)

    groups_file = data_dir / "groups.txt"
    if not groups_file.exists():
        logger.error("❌ File groups.txt tidak ditemukan")
        sys.exit(1)

    messages_dir = data_dir / "messages"
    if not messages_dir.exists() or not messages_dir.is_dir():
        logger.error("❌ Folder messages/ tidak ditemukan")
        sys.exit(1)

    message_files = list(messages_dir.glob("*.txt"))
    if not message_files:
        logger.error("❌ Tidak ada template pesan di folder messages/")
        sys.exit(1)


async def run_scheduled() -> None:
    """Jalankan bot dengan penjadwalan."""
    validate_environment()
    bot = BotRunner()

    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info("🕒 Mulai sesi pada %s", current_time)

            await bot.initialize()
            await bot.run()
            await bot.cleanup()

            # Random interval antara 1.1-1.3 jam
            interval = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
            logger.info("⏳ Menunggu %.1f jam untuk sesi berikutnya", interval / 3600)
            await asyncio.sleep(interval)

        except (AuthError, ConfigError) as e:
            logger.error("❌ Error fatal: %s", str(e))
            break

        except TelegramError as e:
            logger.error("❌ Error Telegram: %s", str(e))
            # Tunggu 5 menit sebelum retry jika error
            await asyncio.sleep(300)
            continue

        except Exception as e:
            logger.exception("❌ Error tidak terduga: %s", str(e))
            break


if __name__ == "__main__":
    try:
        # Start web server untuk keep-alive
        keep_alive()
        # Jalankan bot dengan penjadwalan
        asyncio.run(run_scheduled())
    except KeyboardInterrupt:
        logger.info("👋 Bot dihentikan")
        sys.exit(0)
