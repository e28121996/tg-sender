# Telegram Sender Bot

Bot untuk mengirim pesan ke grup Telegram menggunakan user account.

## Setup di Replit

1. **Generate Session String**
   ```bash
   python get_session.py
   ```
   Ikuti instruksi untuk mendapatkan session string dan credentials.

2. **Setup Environment Variables**
   - Buka project di Replit
   - Klik Tools > Secrets
   - Add secrets berikut:
     ```
     REPLIT_API_ID=your_api_id
     REPLIT_API_HASH=your_api_hash
     REPLIT_PHONE=your_phone
     REPLIT_SESSION=your_session_string
     ```

3. **Setup Data**
   - Buat folder `data`
   - Buat file `data/groups.txt` berisi daftar grup
   - Buat folder `data/messages` berisi template pesan

4. **Run Bot**
   - Klik tombol Run
   - Bot akan mulai berjalan
   - Web server akan aktif untuk keep-alive

## Struktur Data

### groups.txt

