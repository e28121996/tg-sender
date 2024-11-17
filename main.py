"""Script utama untuk menjalankan bot Telegram."""

import asyncio
import logging
import signal
from typing import NoReturn

from src.core import BotRunner
from src.utils.logger import get_logger
from src.web import keep_alive

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
    loop.create_task(bot.stop())


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
