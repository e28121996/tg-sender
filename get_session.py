"""Script untuk generate session string."""

import asyncio
import logging
import os
from getpass import getpass

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

# Setup basic logging
logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def get_input(prompt: str, is_secret: bool = False) -> str:
    """Get input dengan handling untuk secret."""
    while True:
        value = getpass(prompt) if is_secret else input(prompt)
        if value.strip():
            return value.strip()
        logger.error("❌ Input tidak boleh kosong!")


async def main() -> None:
    """Main function untuk generate session."""
    logger.info("\n🔑 Generate Session String untuk Bot\n")

    try:
        # Get credentials
        api_id = int(get_input("API ID: "))  # Convert ke integer
        api_hash = get_input("API Hash: ", is_secret=True)
        phone = get_input("Nomor Telepon (format: +628xxx): ")

        # Create client
        logger.info("\n📱 Mencoba login ke Telegram...")
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            await client.connect()

            # Request kode OTP jika belum login
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                code = get_input("\n📲 Masukkan kode OTP: ")
                await client.sign_in(phone, code)

            # Get session string
            session_str = client.session.save()

            # Log hasil
            logger.info("\n✅ Berhasil generate session string!")
            logger.info("\n⚠️ SIMPAN INFORMASI INI DI REPLIT SECRETS:")
            logger.info("\nAPI_ID = %s", api_id)  # Sesuai config.py
            logger.info("API_HASH = %s", api_hash)  # Sesuai config.py
            logger.info("PHONE_NUMBER = %s", phone)  # Sesuai config.py
            logger.info("SESSION_STRING = %s", session_str)  # Sesuai config.py

            logger.info("\n📝 LANGKAH SETUP DI REPLIT:")
            logger.info("1. Buka project di Replit")
            logger.info("2. Klik Tools > Secrets")
            logger.info("3. Add secret untuk setiap variabel di atas")
            logger.info("4. Restart Repl")
            logger.info("\n🚀 Bot siap dijalankan!")

    except ValueError:
        logger.info("\n❌ Error: API ID harus berupa angka")
    except Exception:
        logger.exception("\n❌ Error saat generate session")


if __name__ == "__main__":
    # Clear screen
    os.system("cls" if os.name == "nt" else "clear")

    logger.info("🔐 TELEGRAM SESSION GENERATOR")
    logger.info("=" * 30)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n👋 Generator dihentikan")
    except Exception:
        logger.exception("\n❌ Error fatal")
