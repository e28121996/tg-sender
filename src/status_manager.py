"""Modul untuk mengelola status.json."""

import json
import random
import time
from pathlib import Path
from typing import Any, TypedDict

from .exceptions import StatusError
from .logger import setup_logger

logger = setup_logger(__name__)

DATA_DIR = Path("data")
STATUS_FILE = DATA_DIR / "status.json"


class SlowModeInfo(TypedDict):
    """Format data slowmode."""

    duration: int  # Durasi dalam detik
    expires_at: float  # UNIX timestamp kapan slowmode berakhir


class Status(TypedDict):
    """Format status.json."""

    groups: list[str]  # Daftar grup
    messages: list[str]  # Template pesan
    blacklist: dict[str, str]  # {group: reason}
    slowmode: dict[str, SlowModeInfo]  # {group: info}
    flood_wait_history: list[tuple[float, int]]  # [(timestamp, seconds), ...]


def _validate_status(data: Any) -> Status:
    """Validasi struktur status dari JSON."""
    if not isinstance(data, dict):
        raise ValueError("Status harus berupa dict")

    required = {"groups", "messages", "blacklist", "slowmode", "flood_wait_history"}
    missing = {key for key in required if key not in data}
    if missing:
        raise ValueError(f"Status tidak memiliki keys: {missing}")

    return Status(
        groups=data["groups"],
        messages=data["messages"],
        blacklist=data["blacklist"],
        slowmode=data["slowmode"],
        flood_wait_history=data["flood_wait_history"],
    )


class StatusManager:
    """Kelas untuk mengelola status.json."""

    def __init__(self) -> None:
        """Inisialisasi StatusManager."""
        self._status = self._load_status()

    def _load_status(self) -> Status:
        """Load status dari file."""
        try:
            # Load groups dan messages
            groups = self._load_groups()
            messages = self._load_messages()

            # Load atau buat status.json
            if STATUS_FILE.exists():
                with open(STATUS_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                    status = _validate_status(data)
                    # Update dengan groups dan messages terbaru
                    status["groups"] = groups
                    status["messages"] = messages
                    return status

            # Status default jika file belum ada
            return {
                "groups": groups,
                "messages": messages,
                "blacklist": {},
                "slowmode": {},
                "flood_wait_history": [],
            }

        except Exception as e:
            logger.error("❌ Error load status: %s", str(e))
            raise StatusError("Gagal load status") from e

    def _save_status(self) -> None:
        """Simpan status ke file."""
        try:
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._status, f, indent=2)
        except Exception as e:
            logger.error("❌ Error save status: %s", str(e))

    def get_active_groups(self) -> list[str]:
        """Ambil daftar grup yang aktif."""
        # Selalu cleanup sebelum mengambil grup aktif
        self._cleanup()

        current_time = time.time()
        active = [
            group
            for group in self._status["groups"]
            if group not in self._status["blacklist"]
            and (
                group not in self._status["slowmode"]
                or self._status["slowmode"][group]["expires_at"] <= current_time
            )
        ]

        # Log status setelah cleanup
        logger.info(
            "📊 Status grup: %d total, %d blacklist, %d slowmode, %d aktif",
            len(self._status["groups"]),
            len(self._status["blacklist"]),
            len(self._status["slowmode"]),
            len(active),
        )
        return active

    def add_slowmode(self, group: str, duration: int) -> None:
        """Add group to slowmode."""
        self._status["slowmode"][group] = {
            "duration": duration,
            "expires_at": time.time() + duration,
        }
        self._save_status()
        logger.info("⏳ %s: Slowmode %d detik", group, duration)

    def add_to_blacklist(self, group: str, reason: str) -> None:
        """Tambahkan grup ke blacklist."""
        if group not in self._status["blacklist"]:
            self._status["blacklist"][group] = reason
            self._save_status()
            logger.info("⛔ %s: Blacklist - %s", group, reason)

    def get_random_message(self) -> str:
        """Ambil pesan secara acak dari daftar template."""
        messages = self._status["messages"]
        if not messages:
            raise StatusError("Tidak ada template pesan tersedia")
        return random.choice(messages)

    def should_pause_globally(self) -> bool:
        """Cek apakah perlu pause global."""
        current_time = time.time()
        recent_floods = [
            t
            for t, _ in self._status["flood_wait_history"]
            if current_time - t < 3600  # 1 jam
        ]
        return len(recent_floods) >= 3

    def get_backoff_delay(self, retry: int) -> float:
        """Get exponential backoff delay."""
        return float(2**retry)  # 1, 2, 4 seconds

    def add_flood_wait(self, seconds: int) -> None:
        """Catat FloodWait ke history."""
        current_time = time.time()
        self._status["flood_wait_history"].append((current_time, seconds))
        self._save_status()  # Langsung save tanpa cleanup

    def _cleanup(self) -> None:
        """Bersihkan data yang expired."""
        current_time = time.time()
        changes = False

        # Cleanup slowmode
        before_slowmode = len(self._status["slowmode"])
        self._status["slowmode"] = {
            group: info
            for group, info in self._status["slowmode"].items()
            if info["expires_at"] > current_time
        }
        after_slowmode = len(self._status["slowmode"])

        # Cleanup flood history
        before_flood = len(self._status["flood_wait_history"])
        self._status["flood_wait_history"] = [
            (t, s)
            for t, s in self._status["flood_wait_history"]
            if current_time - t < 3600  # 1 jam
        ]
        after_flood = len(self._status["flood_wait_history"])

        # Log dan save hanya jika ada perubahan
        if before_slowmode != after_slowmode:
            logger.info(
                "🧹 Cleanup %d slowmode yang expired", before_slowmode - after_slowmode
            )
            changes = True

        if before_flood != after_flood:
            logger.info(
                "🧹 Cleanup %d flood history yang expired", before_flood - after_flood
            )
            changes = True

        if changes:
            self._save_status()

    def _load_messages(self) -> list[str]:
        """Load template pesan dari folder messages/."""
        messages_dir = DATA_DIR / "messages"
        messages: list[str] = []

        try:
            # Load semua file .txt dari folder messages/
            for file in messages_dir.glob("*.txt"):
                try:
                    content = file.read_text(encoding="utf-8").strip()
                    if content:
                        messages.append(content)
                except Exception as e:
                    logger.error("❌ Error load template %s: %s", file.name, str(e))

            if not messages:
                raise StatusError("Tidak ada template pesan tersedia")

            return messages

        except Exception as e:
            logger.error("❌ Error load templates: %s", str(e))
            raise StatusError("Gagal load template pesan") from e

    def _load_groups(self) -> list[str]:
        """Load daftar grup dari groups.txt."""
        groups_file = DATA_DIR / "groups.txt"
        try:
            content = groups_file.read_text(encoding="utf-8")
            groups = [line.strip() for line in content.splitlines() if line.strip()]

            if not groups:
                raise StatusError("File groups.txt kosong")

            return groups

        except Exception as e:
            logger.error("❌ Error load groups: %s", str(e))
            raise StatusError("Gagal load daftar grup") from e
