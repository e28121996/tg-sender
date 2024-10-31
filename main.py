"""Main entry point untuk aplikasi."""

import asyncio
import os
import sys
from pathlib import Path

from src.bot_runner import BotRunner
from src.exceptions import AuthError, ConfigError, TelegramError
from src.logger import setup_logger

logger = setup_logger(name="telegram_sender")


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


async def main() -> None:
    """Entry point utama."""
    validate_environment()
    bot = BotRunner()

    try:
        await bot.initialize()
        await bot.run()

    except (AuthError, ConfigError) as e:
        logger.error("❌ Error fatal: %s", str(e))
        sys.exit(1)

    except TelegramError as e:
        logger.error("❌ Error Telegram: %s", str(e))
        sys.exit(1)

    except Exception as e:
        logger.exception("❌ Error tidak terduga: %s", str(e))
        sys.exit(1)

    finally:
        await bot.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot dihentikan")
        sys.exit(0)
