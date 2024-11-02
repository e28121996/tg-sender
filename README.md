# FITUR UTAMA

## 1. Penggunaan Akun
* Menggunakan akun pengguna Telegram (bukan API bot)
* Session string dari environment variable
* Validasi session saat startup

## 2. Penyimpanan Data
* File status.json untuk menyimpan status dan data
* Format: groups, messages, blacklist, slowmode
* Cache untuk status slowmode dan blacklist
* Validasi struktur dengan TypedDict
* Auto save saat perubahan

## 3. Mekanisme Pengiriman
* Batch 4 pesan dengan interval 4±2 detik
* Jeda 15±2 detik antar batch
* Template pesan random untuk setiap pengiriman
* Random interval 1.1-1.3 jam antar sesi

## 4. Blacklist System
* Auto blacklist untuk error fatal
* Permanent storage di status.json
* Alasan blacklist disimpan
* Skip grup yang di-blacklist
* Error yang di-blacklist:
  - ChatWriteForbiddenError: Tidak bisa kirim pesan
  - UserBannedInChannelError: Akun dibanned
  - ChannelPrivateError: Grup private
  - ChatAdminRequiredError: Butuh hak admin
  - UsernameInvalidError: Format username invalid
  - UsernameNotOccupiedError: Username tidak ada
  - ChatRestrictedError: Grup dibatasi
  - ChatGuestSendForbiddenError: Guest tidak boleh kirim
  - PeerIdInvalidError: ID grup invalid
  - MessageTooLongError: Pesan terlalu panjang
  - MessageNotModifiedError: Pesan tidak berubah
  - ValueError: Link tidak valid

## 5. Slowmode Handling
* Deteksi otomatis dari SlowModeWaitError
* Temporary storage dengan expiry time
* Auto cleanup yang sudah expired
* Skip grup selama durasi slowmode
* Format penyimpanan:
  - duration: Durasi dalam detik
  - expires_at: Timestamp berakhir

## 6. Sistem Logging
* Log ke stdout saja
* Format: timestamp - message (max 100 chars)
* Emoji untuk status visual

# ALUR KERJA DETAIL

## 1. Proses Startup
1. Start web server untuk keep-alive
2. Validasi environment variables
3. Validasi struktur folder dan file
4. Setup logging
5. Create instance BotRunner

## 2. Proses Inisialisasi
1. Setup Telegram client dengan session string
2. Validasi autentikasi session
3. Load status.json
4. Load daftar grup dan template pesan
5. Setup message sender

## 3. Proses Pre-send
1. Cleanup slowmode yang expired
2. Update status.json jika ada perubahan
3. Hitung statistik grup:
   - Total grup
   - Jumlah blacklist
   - Jumlah slowmode
   - Grup aktif
4. Filter grup aktif (non-blacklist & non-slowmode)

## 4. Proses Pengiriman
1. Bagi grup aktif menjadi batch @4
2. Untuk setiap batch:
   - Log info batch
   - Untuk setiap grup:
     * Pilih template random
     * Kirim pesan
     * Handle error
     * Delay 4±2 detik
   - Delay 15±2 detik ke batch berikutnya
3. Log statistik hasil

## 5. Error Handling
1. Jika SlowModeWaitError:
   - Add ke slowmode + expiry
   - Skip grup sementara

2. Jika FloodWaitError:
   - Retry dengan delay
   - Skip jika gagal

3. Jika Error Fatal:
   - Add ke blacklist + alasan
   - Skip grup permanen

## 6. Proses Interval
1. Log statistik final
2. Generate random interval (1.1-1.3 jam)
3. Sleep sampai sesi berikutnya

## 7. Error Recovery
1. Jika error fatal: break loop
2. Jika error Telegram: retry 5 menit
3. Cleanup resources
4. Log error

## 8. Proses Shutdown
1. Disconnect Telegram client
2. Clear resources
3. Exit program

