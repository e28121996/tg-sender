# Telegram Auto Sender
Bot untuk mengirim pesan otomatis ke grup Telegram.

## Struktur Folder
```
├── data/
│   ├── groups.txt       # Daftar URL grup
│   ├── messages/        # Template pesan
│   │   ├── msg1.txt
│   │   └── msg2.txt
│   └── status.json     # Status blacklist & slowmode
├── docs/
│   ├── README.md       # Dokumentasi utama
│   ├── FEATURES.md     # Fitur detail
│   └── WORKFLOW.md     # Alur kerja
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── bot.py
│   │   ├── sender.py
│   │   └── client.py
│   ├── utils/
│   │   ├── __init__.py 
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── status.py
│   └── web/
│       ├── __init__.py
│       └── keep_alive.py
├── main.py           # Entry point
├── .cursorrules      # Cursor rules
├── .env.example      # Contoh environment variables
├── .gitignore        # Git ignore
├── get_session.py    # Script untuk mendapatkan session string
├── pyproject.toml    # Pyproject file
├── render.yaml       # Render file
└── requirements.txt  # Dependencies
```

## Quick Start
1. Copy `.env.example` ke `.env`
2. Isi kredensial Telegram
3. Tambahkan grup di `data/groups.txt`
4. Tambahkan template di `data/messages/`
5. Jalankan `python main.py`

## Dokumentasi
- [Fitur Detail](docs/FEATURES.md)
- [Alur Kerja](docs/WORKFLOW.md)
