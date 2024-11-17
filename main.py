"""Script utama untuk menjalankan bot Telegram."""

import asyncio
import logging
import signal
import sys
from typing import NoReturn

from src.core import BotRunner
from src.utils.logger import get_logger
from src.web import keep_alive
from src.web.keep_alive import shutdown_server

# Konfigurasi logging sekali saja
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log",
)

logger = get_logger(__name__)


def handle_shutdown(bot: BotRunner, loop: asyncio.AbstractEventLoop) -> None:
    """Menangani shutdown dengan aman."""
    if not bot._running:  # Hindari multiple shutdown
        return
    logger.info("Menerima sinyal shutdown...")

    try:
        # Batalkan semua task yang sedang berjalan
        for task in asyncio.all_tasks(loop):
            if task is not asyncio.current_task():
                task.cancel()

        # Jalankan shutdown bot
        loop.create_task(bot.stop())

        # Tunggu semua task selesai
        loop.run_until_complete(
            asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True)
        )

        # Hentikan web server
        shutdown_server()

        # Hentikan event loop
        loop.stop()
        loop.close()

    except Exception as e:
        logger.error("Error saat shutdown: %s", str(e))
    finally:
        # Pastikan program benar-benar berhenti
        sys.exit(0)


async def run_bot() -> None:
    """Menjalankan bot dalam event loop."""
    bot = BotRunner()
    loop = asyncio.get_running_loop()

    # Setup signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: handle_shutdown(bot, loop))

    try:
        await bot.start()
    except Exception as e:
        logger.error("Error fatal: %s", str(e))
        raise
    finally:
        logger.info("Bot berhenti")


def main() -> NoReturn:
    """Fungsi utama untuk menjalankan bot."""
    # Start web server
    keep_alive()
    logger.info("Web server started")

    # Run bot
    while True:
        try:
            asyncio.run(run_bot())
        except Exception as e:
            logger.error("Error dalam main loop: %s", str(e))
            asyncio.run(asyncio.sleep(5))


if __name__ == "__main__":
    main()
