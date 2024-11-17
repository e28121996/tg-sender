.PHONY: run dev clean setup session

# Jalankan bot
run:
	python main.py

# Format dan periksa kode
dev:
	ruff format .
	ruff check .
	mypy .

# Hapus file cache Python
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "status.json" -delete
	find . -type f -name "bot.log" -delete

# Buat struktur folder dan file
setup:
	mkdir -p data/messages
	touch data/groups.txt
	echo "# Daftar URL grup (satu per baris)\n# Contoh: t.me/namagrup" > data/groups.txt
	
	# Template 1 - Contoh format panduan verifikasi
	echo "# INI HANYA CONTOH TEMPLATE - SILAKAN SESUAIKAN ISI PESAN\n\n🔰 *PANDUAN VERIFIKASI KYC* 🔰\n\nUntuk meningkatkan keamanan akun, mohon lengkapi data berikut:\n\n✅ Foto KTP/SIM/Passport\n✅ Foto Selfie dengan KTP\n✅ Nomor Rekening Bank\n✅ Nama sesuai KTP\n\n*Kirim data ke admin:*\nt.me/adminKYC\n\n# Catatan: Ganti t.me/adminKYC dengan username admin Anda" > data/messages/msg1.txt
	
	# Template 2 - Contoh format informasi manfaat
	echo "# INI HANYA CONTOH TEMPLATE - SILAKAN SESUAIKAN ISI PESAN\n\n📋 *VERIFIKASI AKUN - KYC* 📋\n\nPenting❗\nVerifikasi akun diperlukan untuk:\n• Keamanan transaksi\n• Pencairan dana cepat\n• Bonus member verified\n\n*Hubungi admin untuk verifikasi:*\nt.me/adminKYC\n\n# Catatan: Ganti t.me/adminKYC dengan username admin Anda" > data/messages/msg2.txt 
	
	# Template 3 - Contoh format prosedur
	echo "# INI HANYA CONTOH TEMPLATE - SILAKAN SESUAIKAN ISI PESAN\n\n⚠️ *INFORMASI KYC (KNOW YOUR CUSTOMER)* ⚠️\n\nSegera verifikasi akun Anda:\n1. Foto KTP jelas\n2. Selfie dengan KTP\n3. Nomor rekening aktif\n\nProses verifikasi 5-10 menit✅\n\n*Chat admin:*\nt.me/adminKYC\n\n# Catatan: Ganti t.me/adminKYC dengan username admin Anda" > data/messages/msg3.txt
	
	@echo "Setup selesai. Struktur folder telah dibuat:"
	@echo "data/"
	@echo "├── groups.txt"
	@echo "└── messages/"
	@echo "    ├── msg1.txt (Template panduan verifikasi)"
	@echo "    ├── msg2.txt (Template informasi manfaat)"
	@echo "    └── msg3.txt (Template prosedur)"
	@echo "\nPENTING: Template pesan di atas hanya contoh."
	@echo "Silakan edit file di folder data/messages sesuai kebutuhan Anda."

# Buat session string Telegram
session:
	@echo "╔════════════════════════════════════════╗"
	@echo "║       🔐 MEMBUAT SESSION STRING        ║"
	@echo "╚════════════════════════════════════════╝"
	@echo ""
	@echo "📋 PERSIAPKAN DATA BERIKUT:"
	@echo "1. API ID     (dari my.telegram.org)"
	@echo "2. API HASH   (dari my.telegram.org)"
	@echo "3. No Telepon (format: +628xxx)"
	@echo ""
	@echo "🚫 PASTIKAN MENGGUNAKAN AKUN UTAMA"
	@echo "🚫 JANGAN GUNAKAN AKUN BOT/TEST"
	@echo ""
	python -c "from telethon.sync import TelegramClient; \
		from telethon.sessions import StringSession; \
		print('📱 Session string Anda:'); \
		print(StringSession.save(TelegramClient(StringSession(), \
		input('📍 API ID: '), \
		input('📍 API Hash: ')).start(phone=input('📍 Nomor Telepon: '))))"
	@echo ""
	@echo "✅ Session string berhasil dibuat!"
	@echo ""
	@echo "📝 LANGKAH SELANJUTNYA:"
	@echo "1. Copy session string di atas"
	@echo "2. Simpan ke environment variable TELEGRAM_SESSION"
	@echo "3. Simpan API_ID ke TELEGRAM_API_ID"
	@echo "4. Simpan API_HASH ke TELEGRAM_API_HASH"
	@echo ""
	@echo "🔒 JANGAN BAGIKAN SESSION STRING KE SIAPAPUN"
	@echo "🔒 JANGAN SCREENSHOT ATAU SIMPAN DI CLOUD"