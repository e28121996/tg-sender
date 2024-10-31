"""Script untuk mendapatkan session string."""

from pathlib import Path
from typing import NoReturn

from telethon.errors import (
    AuthKeyUnregisteredError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession
from telethon.sync import TelegramClient


def exit_with_error(message: str) -> NoReturn:
    """Keluar dengan pesan error."""
    print(f"\n❌ Error: {message}")
    exit(1)


def get_input(prompt: str, required: bool = True) -> str:
    """Dapatkan input dari user."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("❌ Input tidak boleh kosong!")


def create_env_file(api_id: str, api_hash: str, phone: str, session: str) -> None:
    """Buat file .env dengan kredensial."""
    env_path = Path(".env")

    env_content = [
        "# Telegram API Credentials",
        f"API_ID={api_id}",
        f"API_HASH={api_hash}",
        f"PHONE_NUMBER={phone}",
        f"SESSION_STRING={session}",
        "",
        "# Logging",
        "LOG_LEVEL=INFO",
    ]

    env_path.write_text("\n".join(env_content))
    print(f"\n✅ File .env berhasil dibuat di: {env_path.absolute()}")


try:
    print("\n🔑 Setup Telegram Client")
    print("------------------------")

    # Input API credentials
    api_id = get_input("Masukkan API_ID: ")
    api_hash = get_input("Masukkan API_HASH: ")
    phone = get_input("Masukkan nomor telepon (format: +628xxx): ")

    try:
        api_id_int = int(api_id)
    except ValueError:
        exit_with_error("API_ID harus berupa angka")

    print("\n📱 Memulai proses login...")
    print("Anda akan menerima kode verifikasi via Telegram\n")

    with TelegramClient(StringSession(), api_id_int, api_hash) as client:
        # Login dan dapatkan session string
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            code = get_input("Masukkan kode verifikasi: ")
            try:
                client.sign_in(phone, code)
            except SessionPasswordNeededError:
                password = get_input("Masukkan password 2FA: ")
                client.sign_in(password=password)

        # Dapatkan session string
        session_string = client.session.save()
        print("\n✅ Login berhasil!")

        # Buat file .env
        create_env_file(api_id, api_hash, phone, session_string)
        print("\n!!! PENTING: Jaga kerahasiaan file .env!")

except (
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    AuthKeyUnregisteredError,
) as e:
    exit_with_error(str(e))
except OSError as e:
    exit_with_error(f"Error sistem: {e}")
except KeyboardInterrupt:
    print("\n\nDibatalkan oleh user")
    exit(1)
