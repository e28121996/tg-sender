"""Modul untuk menangani operasi klien Telegram."""

import asyncio
from typing import Any, Generator, Union

from telethon import TelegramClient
from telethon.errors import AuthRestartError, FloodWaitError, SessionPasswordNeededError
from telethon.tl.types import InputPeerChannel, InputPeerChat, InputPeerUser

from .config import CONFIG
from .logger import setup_logger

logger = setup_logger(__name__, CONFIG.logging["file"])

EntityLike = Union[InputPeerUser, InputPeerChannel, InputPeerChat, str]


class TelegramSenderClient:
    def __init__(self, api_id: int, api_hash: str, phone: str):
        self.client: Any = TelegramClient("anon", api_id, api_hash)
        self.phone = phone
        logger.info("TelegramSenderClient diinisialisasi")

    async def start(self, password: str) -> None:
        logger.info(f"Mencoba memulai klien Telegram dengan nomor: {self.phone}")
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                await self.client.start(
                    phone=self.phone, code_callback=self.code_callback
                )

                if not await self.client.is_user_authorized():
                    await self.client.sign_in(password=password)

                logger.info("Klien Telegram berhasil dimulai.")
                return
            except AuthRestartError:
                logger.warning(
                    f"AuthRestartError terjadi. Percobaan {attempt + 1} dari {max_attempts}"
                )
                if attempt == max_attempts - 1:
                    raise
                await asyncio.sleep(5)  # Tunggu 5 detik sebelum mencoba lagi
            except SessionPasswordNeededError:
                await self.client.sign_in(password=password)
                logger.info("Klien Telegram berhasil dimulai dengan 2FA.")
                return
            except Exception as e:
                logger.error(f"Gagal memulai klien Telegram: {e}")
                raise

    async def stop(self) -> None:
        if self.client.is_connected():
            await self.client.disconnect()
        logger.info("Klien Telegram dihentikan")

    async def send_message(self, group_link: str, message: str) -> None:
        try:
            entity = await self.client.get_input_entity(group_link)
            await self.client.send_message(entity, message)
            logger.debug(f"Pesan berhasil dikirim ke {group_link}")  # Ubah ke debug
        except FloodWaitError as e:
            logger.warning(f"FloodWaitError: Harus menunggu {e.seconds} detik")
            raise
        except Exception as e:
            logger.error(f"Gagal mengirim pesan ke {group_link}: {e}")
            raise

    async def is_user_authorized(self) -> bool:
        return await self.client.is_user_authorized()

    def __await__(self) -> Generator[Any, None, None]:
        return self.start(CONFIG.telegram_password).__await__()

    @staticmethod
    def code_callback() -> str:
        return input("Silakan masukkan kode yang Anda terima: ")
