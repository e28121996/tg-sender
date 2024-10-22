# Bot Pengiriman Pesan Telegram

Bot ini dirancang untuk mengirim pesan ke grup Telegram secara otomatis dan terjadwal.

## Fitur Utama

1. Penggunaan akun pengguna Telegram (bukan API bot)
2. Mengirim pesan ke grup dari daftar di `data/groups.txt`
3. Pengiriman pesan acak dari template di `data/messages/`
4. Pengiriman dalam batch 4 pesan dengan interval 3-5 detik antar pesan
5. Interval 10-20 detik antara batch ke grup berbeda
6. Penjadwalan otomatis setiap 1,1-1,3 jam
7. Operasi asinkron untuk pengiriman paralel
8. Penanganan status grup (blacklist dan slowmode)
9. Manajemen status menggunakan `data/status.json`
10. Konfigurasi menggunakan `config.yaml` dan `.env`
11. Logging komprehensif
12. Caching menggunakan `data/status.json`
13. Penanganan kesalahan dengan mekanisme retry dan blacklisting
14. Pemantauan kinerja dengan metrik
15. Pembatasan laju global untuk menghindari pembatasan Telegram

## Struktur Proyek

- `src/`: Kode sumber utama
  - `__init__.py`: Inisialisasi modul
  - `config.py`: Konfigurasi bot
  - `error_handler.py`: Penanganan kesalahan
  - `logger.py`: Konfigurasi logging
  - `main.py`: Skrip utama
  - `message_sender.py`: Logika pengiriman pesan
  - `scheduler.py`: Penjadwalan tugas
  - `status_manager.py`: Manajemen status grup
  - `telegram_client.py`: Klien Telegram
  - `utils.py`: Fungsi utilitas
- `data/`: File data
  - `groups.txt`: Daftar grup target
  - `messages/`: Template pesan
  - `status.json`: Status grup (blacklist dan slowmode)
- `logs/`: File log
- `config.yaml`: Konfigurasi umum
- `.env`: Informasi sensitif (API credentials)
- `.cursorrules`: Aturan gaya kode

## Penggunaan

1. Pastikan Python 3.11 terinstal
2. Install dependensi: `pip install -r requirements.txt`
3. Sesuaikan konfigurasi di `config.yaml` dan `.env`
4. Jalankan bot: `python src/main.py`

## Konfigurasi

Konfigurasi utama ada di `config.yaml`, termasuk:
- Pengaturan Telegram API
- Interval pengiriman pesan
- Penjadwalan
- Penanganan kesalahan
- Pembatasan laju
- Path file

Kredensial API disimpan di `.env`:
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE_NUMBER`

## Alur Kerja

1. Inisialisasi: Memuat konfigurasi, status, dan koneksi Telegram
2. Penjadwalan: Mengatur waktu pengiriman berikutnya
3. Pengiriman Pesan: Memfilter grup, mengirim dalam batch
4. Penanganan Kesalahan: Retry untuk kesalahan sementara, blacklist untuk permanen
5. Pembaruan Status: Memperbarui status grup setelah pengiriman
6. Logging dan Pemantauan: Mencatat aktivitas dan metrik kinerja

## Penanganan Kesalahan

- Retry dengan backoff untuk kesalahan sementara
- Blacklisting otomatis untuk kesalahan permanen
- Penanganan khusus untuk slowmode

## Pemantauan

Log tersimpan di `logs/bot.log` dengan informasi rinci tentang aktivitas bot.

## Keamanan

- Gunakan akun Telegram yang dedicated untuk bot ini
- Jangan bagikan kredensial API atau file `.env`
- Perhatikan pembatasan laju untuk menghindari pemblokiran oleh Telegram

## Catatan

Proyek ini adalah untuk penggunaan pribadi. Pastikan untuk mematuhi Syarat Layanan Telegram saat menggunakannya.
