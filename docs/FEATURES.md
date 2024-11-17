# FITUR UTAMA

## 1. Penggunaan Akun
* Menggunakan akun pengguna Telegram (bukan API bot)
* Menyimpan kredensial di environment variables:
  - TELEGRAM_API_ID: API ID dari Telegram
  - TELEGRAM_API_HASH: API Hash dari Telegram 
  - TELEGRAM_SESSION: Session string hasil generate
* Validasi kredensial saat startup

## 2. Pengelolaan Data
* Sumber data:
  - Daftar grup (data/groups.txt):
    * Format per baris: URL grup (t.me/namagrup)
    * Satu grup per baris
    * Skip baris kosong
  - Template pesan (data/messages/*.txt):
    * Satu file = satu template
    * Format bebas dalam file
    * Dipilih secara acak saat kirim
    * Mendukung format Markdown

* Status di status.json:
  ```json
  {
    "blacklist": {
      "t.me/grupA": "ChatWriteForbidden",
      "t.me/grupB": "ChannelPrivate"  
    },
    "slowmode": {
      "t.me/grupC": 1679123456
    }
  }
  ```
* Pengelolaan status:
  - Blacklist: Permanen dengan format "url": "alasan"
  - Slowmode: Sementara dengan format "url": timestamp_expired
  - Pembersihan otomatis slowmode yang kadaluarsa
  - Penyimpanan otomatis saat ada perubahan

## 3. Mekanisme Pengiriman
* Batch 4 pesan dengan interval 5 detik
* Jeda 15 detik antar batch
* Template pesan acak untuk setiap pengiriman
* Interval acak 1,1-1,3 jam antar sesi

## 4. Penanganan Error
* Penanganan Slowmode:
  - Deteksi otomatis dari SlowModeWaitError
  - Penyimpanan sementara di status.json
  - Pembersihan otomatis yang kadaluarsa
  - Lewati grup selama durasi slowmode
  - Format penyimpanan: "url": timestamp_expired

* Sistem Blacklist:
  - Penyimpanan permanen di status.json
  - Alasan blacklist disimpan
  - Lewati grup yang masuk blacklist
  - Error yang masuk blacklist:
    - ChatWriteForbiddenError: Tidak bisa mengirim pesan ke grup
    - UserBannedInChannelError: Akun telah dibanned
    - ChannelPrivateError: Grup bersifat private
    - ChatAdminRequiredError: Membutuhkan hak admin
    - UsernameInvalidError: Format username tidak valid
    - UsernameNotOccupiedError: Username tidak ditemukan
    - ChatRestrictedError: Grup dibatasi
    - ChatGuestSendForbiddenError: Tamu tidak boleh mengirim pesan
    - PeerIdInvalidError: ID grup tidak valid
    - InvalidURLError: Format URL tidak valid
    - URLNotFoundError: URL tidak ditemukan
    - ForbiddenError: Diblokir atau tidak memiliki akses