"""Script untuk generate session string Telegram."""

import logging
from typing import cast

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_session() -> str | None:
    """Membuat dan mengembalikan session string Telegram.

    Returns:
        str | None: Session string jika berhasil, None jika dibatalkan
    """
    # Minta input dari pengguna
    api_id = int(input("Masukkan API_ID: "))  # Convert ke int
    api_hash = input("Masukkan API_HASH: ")
    phone = input("Masukkan nomor telepon: ")

    # Konfirmasi nomor telepon
    confirm = input(f"Konfirmasi nomor {phone} [y/n]: ")
    if confirm.lower() != "y":
        logger.info("Dibatalkan oleh pengguna")
        return None

    # Buat client dan dapatkan session string
    with TelegramClient(StringSession(), api_id, api_hash) as client:
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            client.sign_in(phone)

        session_string = cast(str, StringSession.save(client.session))

        logger.info("\nIni session string Anda:")
        logger.info(session_string)
        logger.info("\nSimpan string ini dengan aman!")

        return session_string


if __name__ == "__main__":
    get_session()
