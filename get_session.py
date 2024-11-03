"""Script untuk mendapatkan session string."""

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

# Masukkan API credentials
api_id = input("Enter API ID: ")
api_hash = input("Enter API Hash: ")
phone = input("Enter Phone Number: ")

# Buat client dan dapatkan session string
with TelegramClient(StringSession(), api_id, api_hash) as client:
    # Login jika belum
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input("Enter the code you received: "))

    # Print session string
    print("\nYour session string is:\n")
    print(client.session.save())
    print("\nPlease store it safely!")
