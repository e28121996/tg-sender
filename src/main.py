"""Modul utama untuk bot pengirim pesan Telegram."""

import asyncio
import signal
import sys
from typing import Callable, Dict, List, Set

from telethon.errors import AuthRestartError, SessionPasswordNeededError

from .config import CONFIG
from .error_handler import ErrorHandler
from .logger import setup_logger
from .message_sender import MessageSender
from .scheduler import Scheduler
from .status_manager import StatusManager
from .telegram_client import TelegramSenderClient
from .utils import create_pid_file, remove_pid_file

logger = setup_logger(__name__, CONFIG.logging["file"])

shutdown_event = asyncio.Event()
shutdown_in_progress = False
shutdown_tasks: Dict[signal.Signals, asyncio.Task] = {}


async def load_groups() -> List[str]:
    """Muat daftar grup dari file."""
    try:
        with open(CONFIG.groups_file, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"File grup tidak ditemukan: {CONFIG.groups_file}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"Gagal membaca file grup: {e}")
        sys.exit(1)


async def shutdown(sig: int, loop: asyncio.AbstractEventLoop) -> None:
    """Cleanup tasks tied to the service's shutdown."""
    global shutdown_in_progress
    if shutdown_in_progress:
        return
    shutdown_in_progress = True

    sig_name = signal.Signals(sig).name
    logger.info(f"Menerima sinyal exit {sig_name}...")
    shutdown_event.set()
    tasks: Set[asyncio.Task] = {
        t for t in asyncio.all_tasks() if t is not asyncio.current_task()
    }

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


def signal_handler(sig: int) -> None:
    """Handler untuk sinyal shutdown."""
    loop = asyncio.get_running_loop()
    shutdown_tasks[signal.Signals(sig)] = loop.create_task(shutdown(sig, loop))


async def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    logger.info("Memulai bot pengirim pesan Telegram")

    if not create_pid_file():
        logger.error("Instansi bot lain sedang berjalan. Keluar.")
        return

    client = None
    try:
        groups = await load_groups()
        logger.info(f"Berhasil memuat {len(groups)} grup")

        status_manager = StatusManager()
        error_handler = ErrorHandler(status_manager)

        client = TelegramSenderClient(
            CONFIG.api_id, CONFIG.api_hash, CONFIG.phone_number
        )

        try:
            await client.start(CONFIG.telegram_password)
        except (AuthRestartError, SessionPasswordNeededError) as e:
            logger.error(f"Gagal mengautentikasi: {e}")
            return
        except Exception as e:
            logger.error(f"Kesalahan tidak terduga saat memulai klien: {e}")
            return

        message_sender = MessageSender(client, status_manager, error_handler)
        scheduler = Scheduler()

        scheduler.set_task(message_sender.send_messages, groups)

        logger.info("Memulai penjadwalan pengiriman pesan")
        loop = asyncio.get_running_loop()
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:

            def create_signal_handler(sig: signal.Signals = s) -> Callable[[], None]:
                def signal_handler_wrapper() -> None:
                    signal_handler(sig)

                return signal_handler_wrapper

            loop.add_signal_handler(s, create_signal_handler())

        try:
            await scheduler.run()
        except asyncio.CancelledError:
            logger.info("Scheduler dibatalkan")
        except Exception as e:
            logger.error(f"Kesalahan tidak terduga dalam scheduler: {e}")
        finally:
            await cleanup(client)

    except asyncio.CancelledError:
        logger.info("Program dibatalkan")
    except KeyboardInterrupt:
        logger.info("Menerima sinyal interupsi. Menghentikan bot...")
    except Exception as e:
        logger.error(f"Terjadi kesalahan yang tidak terduga: {e}")
    finally:
        logger.info("Membersihkan dan menutup koneksi...")
        if client:
            await client.stop()
        remove_pid_file()
        logger.info("Bot dihentikan")


async def cleanup(client: TelegramSenderClient | None) -> None:
    """Membersihkan dan menutup koneksi."""
    global shutdown_in_progress
    if shutdown_in_progress:
        return
    shutdown_in_progress = True

    logger.info("Membersihkan dan menutup koneksi...")
    if client:
        await client.stop()
    remove_pid_file()
    logger.info("Bot dihentikan")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Terjadi kesalahan: {e}")
    finally:
        logger.info("Program selesai")
