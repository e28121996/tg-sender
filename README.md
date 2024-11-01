# Telegram Message Sender

## Fitur Utama

### 1. Penggunaan Akun
- Menggunakan akun pengguna Telegram (bukan API bot)
- Session string dari environment variable

### 2. Penyimpanan Data
- File status.json untuk menyimpan status dan data
- Cache untuk status slowmode dan blacklist dalam file

### 3. Mekanisme Pengiriman
- Batch 4 pesan dengan interval 4±2 detik
- Jeda 15±2 detik antar batch
- Deteksi otomatis slowmode
- Penanganan FloodWait error sesuai standar Telegram

### 4. Sistem Logging
- Log ke stdout saja
- Format log sederhana dan konsisten

## Alur Kerja Detail

### 1. Inisialisasi
- Load konfigurasi dari env vars termasuk session string
- Setup logging
- Load status.json
- Setup session Telegram
- Load daftar grup dan template

### 2. Pengecekan Grup

#### a. Pre-send Validation
- Cek status blacklist
- Cek status slowmode

#### b. Slowmode Detection
- Catch SlowModeWaitError
- Catat durasi slowmode di status.json
- Skip grup untuk sementara

#### c. FloodWait Handling
- Deteksi FloodWaitError
- Implementasi exponential backoff (2^n seconds)
- Maksimal retry 3x dengan interval meningkat
- Pause global jika terlalu sering

### 3. Penanganan Error

#### Auto Blacklist
- ChatWriteForbiddenError: Tidak ada izin menulis
- UserBannedInChannelError: User dibanned
- ChannelPrivateError: Grup private
- ChatAdminRequiredError: Butuh hak admin
- UsernameInvalidError: Format invalid
- UsernameNotOccupiedError: Username tidak ada
- ValueError: Link tidak valid
- ChatRestrictedError
- ChatGuestSendForbiddenError
- PeerIdInvalidError
- MessageTooLongError
- MessageNotModifiedError

### 4. Proses Pengiriman

#### a. Persiapan
- Filter grup blacklist
- Filter grup slowmode aktif
- Bagi menjadi batch 4 grup

#### b. Eksekusi per Batch
- Pilih template secara acak dari daftar template yang tersedia
- Kirim dengan delay 4±2 detik
- Tunggu 15±2 detik untuk batch berikutnya
- Handle FloodWait dengan backoff strategy

#### c. Error Handling
- Catat error ke log
- Update status grup di status.json
- Lanjut ke grup berikutnya

### 5. Manajemen Status

#### a. Blacklist
- Simpan grup + alasan
- Permanent storage di status.json
- Skip saat pengiriman

#### b. Slowmode
- Catat durasi + waktu berakhir
- Temporary storage di status.json
- Auto cleanup expired entries

### 6. Logging

#### Output
- Log ke stdout saja
- Format log sederhana dan konsisten