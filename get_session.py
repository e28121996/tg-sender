"""Script untuk mendapatkan session string."""

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

# Masukkan API credentials
api_id = input("Enter API ID: ")
api_hash = input("Enter API Hash: ")
phone = input("Enter Phone Number: ")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    client.send_code_request(phone)
    client.sign_in(phone, input("Enter code: "))
    print("Session String:", client.session.save())
