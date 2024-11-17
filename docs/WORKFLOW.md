# ALUR KERJA

## 1. Proses Startup
- Memulai web server untuk keep-alive
- Validasi environment variables
- Validasi struktur folder dan file
- Membuat instance BotRunner

## 2. Proses Inisialisasi
- Menyiapkan Telegram client dengan session string
- Validasi autentikasi session
- Memuat status dari data/status.json:
  * Membuat file baru jika belum ada
  * Validasi format JSON
- Memuat daftar grup dari data/groups.txt
- Memuat template pesan dari data/messages/*.txt
- Menyiapkan pengirim pesan

## 3. Proses Pre-send
- Membersihkan slowmode yang kadaluarsa:
  * Menghapus entri dengan timestamp < waktu_sekarang
- Memperbarui status.json jika ada perubahan
- Menghitung statistik grup:
  * Total grup
  * Jumlah blacklist
  * Jumlah slowmode
  * Grup aktif
- Memfilter grup aktif (non-blacklist & non-slowmode)

## 4. Proses Pengiriman
- Membagi grup aktif menjadi batch @4
- Untuk setiap batch:
  * Mencatat info batch
  * Untuk setiap grup:
    - Memilih template secara acak
    - Mengirim pesan
    - Menangani error
    - Jeda 5 detik
  * Jeda 15 detik ke batch berikutnya
- Mencatat statistik hasil

## 5. Penanganan Error
- Jika SlowModeWaitError:
  * Menghitung timestamp_expired = waktu_sekarang + durasi_error
  * Menambahkan ke slowmode dengan timestamp_expired
  * Lewati grup sementara

- Jika FloodWaitError:
  * Mencoba ulang dengan jeda sesuai error
  * Lewati jika gagal

- Jika Error lainnya:
  * Menambahkan ke blacklist dengan format "url": "alasan_error"
  * Lewati grup secara permanen

## 6. Proses Interval
- Mencatat statistik akhir
- Menghasilkan interval acak (1,1-1,3 jam)
- Istirahat sampai sesi berikutnya

## 7. Proses Shutdown
- Memutuskan koneksi Telegram client
- Membersihkan resources
- Mengakhiri program