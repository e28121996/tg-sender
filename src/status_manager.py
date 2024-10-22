"""Modul untuk mengelola status grup."""

import json
import time
from typing import Any, Dict, Set

from .config import CONFIG
from .logger import setup_logger

logger = setup_logger(__name__, CONFIG.logging["file"])


class StatusManager:
    def __init__(self) -> None:
        self.status_file = CONFIG.status_file
        self.blacklist: Set[str] = set()
        self.slowmode: Dict[str, float] = {}
        self.load_status()
        self.messages_sent = 0
        self.messages_failed = 0
        logger.info("StatusManager diinisialisasi")

    def load_status(self) -> None:
        try:
            with open(self.status_file, "r") as f:
                data: Any = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Data status harus berupa dictionary")

                self.blacklist = set(data.get("blacklist", []))
                if not all(isinstance(item, str) for item in self.blacklist):
                    raise ValueError("Semua item dalam blacklist harus berupa string")

                self.slowmode = {
                    k: v
                    for k, v in data.get("slowmode", {}).items()
                    if isinstance(k, str)
                    and isinstance(v, (int, float))
                    and v > time.time()
                }

                logger.info(
                    f"Status dimuat: {len(self.blacklist)} grup dalam blacklist, {len(self.slowmode)} grup dalam slowmode"
                )
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Kesalahan saat memuat status: {e}. Mereset status.")
            self.blacklist = set()
            self.slowmode = {}
        except FileNotFoundError:
            logger.warning(
                f"File status {self.status_file} tidak ditemukan. Membuat baru."
            )
        finally:
            self.save_status()

    def save_status(self) -> None:
        with open(self.status_file, "w") as f:
            json.dump(
                {
                    "blacklist": list(self.blacklist),
                    "slowmode": self.slowmode,
                },
                f,
                indent=2,
                sort_keys=True,
            )
        logger.info("Status disimpan ke file")

    def add_to_blacklist(self, group: str) -> None:
        """Tambahkan grup ke blacklist."""
        self.blacklist.add(group)
        logger.info(f"Grup {group} ditambahkan ke blacklist")
        self.save_status()

    def add_to_slowmode(self, group: str, duration: int = 3600) -> None:
        expiry_time = time.time() + duration
        self.slowmode[group] = expiry_time
        logger.info(
            f"Grup {group} ditambahkan ke slowmode selama {duration} detik, berakhir pada {time.ctime(expiry_time)}"
        )
        self.save_status()

    def is_blacklisted(self, group: str) -> bool:
        return group in self.blacklist

    def is_in_slowmode(self, group: str) -> bool:
        if group in self.slowmode:
            if self.slowmode[group] > time.time():
                return True
            else:
                del self.slowmode[group]
                logger.info(f"Grup {group} dihapus dari slowmode karena sudah berakhir")
                self.save_status()
        return False

    def clean_expired_slowmode(self) -> None:
        current_time = time.time()
        expired = [
            group
            for group, expire_time in self.slowmode.items()
            if expire_time <= current_time
        ]
        for group in expired:
            del self.slowmode[group]
        if expired:
            self.save_status()
            logger.info(
                f"Membersihkan {len(expired)} entri slowmode yang sudah berakhir: {', '.join(expired)}"
            )

    def log_metrics(self) -> None:
        logger.info(
            f"Metrik kinerja: {self.messages_sent} pesan terkirim, {self.messages_failed} pesan gagal"
        )
        logger.info(
            f"Status grup: {len(self.blacklist)} dalam blacklist, {len(self.slowmode)} dalam slowmode"
        )

    def reset_metrics(self) -> None:
        self.messages_sent = 0
        self.messages_failed = 0
