"""Modul untuk mengelola status.json."""

import json
import time
from pathlib import Path
from typing import Any, Final, cast

from .config import DATA_DIR, GROUPS_FILE
from .exceptions import StatusError
from .logger import setup_logger
from .types import SlowmodeInfo, StatusData, StatusManagerProtocol

logger = setup_logger(name=__name__)

# Konstanta untuk file status
STATUS_FILE: Final[Path] = DATA_DIR / "status.json"

# Default status data
DEFAULT_STATUS: Final[StatusData] = cast(
    StatusData,
    {
        "blacklist": {},
        "slowmode": {},
        "last_updated": 0.0,
    },
)


class StatusManager(StatusManagerProtocol):
    """Class untuk mengelola status.json."""

    def __init__(self) -> None:
        """Inisialisasi status manager."""
        self._status: StatusData = cast(StatusData, DEFAULT_STATUS.copy())
        self._groups: list[str] = []
        self._load_status()
        self._load_groups()

    def _validate_slowmode_info(self, info: Any) -> bool:
        """Validasi format info slowmode."""
        if not isinstance(info, dict):
            return False
        duration: Any = info.get("duration")
        expires_at: Any = info.get("expires_at")
        if not isinstance(duration, int | float):
            return False
        if not isinstance(expires_at, int | float):
            return False
        return True

    def _validate_status_data(self, data: dict[str, Any]) -> StatusData:
        """Validasi dan konversi data status."""
        try:
            # Validasi blacklist
            blacklist: Any = data.get("blacklist", {})
            if not isinstance(blacklist, dict):
                raise StatusError("Format blacklist tidak valid")
            if not all(
                isinstance(k, str) and isinstance(v, str) for k, v in blacklist.items()
            ):
                raise StatusError("Format data blacklist tidak valid")

            # Validasi slowmode
            slowmode: Any = data.get("slowmode", {})
            if not isinstance(slowmode, dict):
                raise StatusError("Format slowmode tidak valid")
            if not all(
                isinstance(k, str) and self._validate_slowmode_info(v)
                for k, v in slowmode.items()
            ):
                raise StatusError("Format data slowmode tidak valid")

            # Validasi last_updated
            last_updated: Any = data.get("last_updated", time.time())
            if not isinstance(last_updated, int | float):
                last_updated = time.time()

            return cast(
                StatusData,
                {
                    "blacklist": blacklist,
                    "slowmode": slowmode,
                    "last_updated": last_updated,
                },
            )

        except (TypeError, KeyError) as e:
            raise StatusError(f"Format data tidak valid: {e}") from e

    def _load_status(self) -> None:
        """Load status dari file."""
        try:
            if not STATUS_FILE.exists():
                logger.warning("⚠️ File status tidak ditemukan, menggunakan default")
                self.save()  # Create file with default data
                return

            json_data: str = STATUS_FILE.read_text()
            data: dict[str, Any] = json.loads(json_data)

            # Validate and convert data
            self._status = self._validate_status_data(data)
            logger.info("✅ Berhasil load status")

        except json.JSONDecodeError as e:
            logger.error("❌ File status corrupt: %s", str(e))
            self._status = cast(StatusData, DEFAULT_STATUS.copy())
            self.save()  # Overwrite corrupt file
        except StatusError as e:
            logger.error("❌ %s", str(e))
            self._status = cast(StatusData, DEFAULT_STATUS.copy())
            self.save()  # Overwrite invalid file
        except Exception as e:
            logger.error("❌ Error saat load status: %s", str(e))
            self._status = cast(StatusData, DEFAULT_STATUS.copy())
            self.save()  # Overwrite problematic file

    def _load_groups(self) -> None:
        """Load daftar grup dari groups.txt."""
        try:
            if not GROUPS_FILE.exists():
                raise StatusError("File groups.txt tidak ditemukan")

            self._groups = GROUPS_FILE.read_text().strip().splitlines()
            logger.info("✅ Berhasil load %d grup", len(self._groups))

        except Exception as e:
            raise StatusError(f"Error saat load groups: {e}") from e

    def get_active_groups(self) -> list[str]:
        """Get list grup aktif (non-blacklist & non-slowmode)."""
        return [
            group
            for group in self._groups
            if group not in self._status["blacklist"]
            and group not in self._status["slowmode"]
        ]

    def get_groups(self) -> list[str]:
        """Get list grup."""
        return self._groups.copy()

    def get_blacklist(self) -> dict[str, str]:
        """Get dict blacklist."""
        return cast(dict[str, str], self._status["blacklist"])

    def get_slowmode(self) -> dict[str, SlowmodeInfo]:
        """Get dict slowmode."""
        return cast(dict[str, SlowmodeInfo], self._status["slowmode"])

    def save(self) -> None:
        """Save status ke file."""
        try:
            self._status["last_updated"] = time.time()
            json_data: str = json.dumps(self._status, indent=2)
            STATUS_FILE.write_text(json_data)
        except Exception as e:
            raise StatusError(f"Error saat save status: {e}") from e

    def add_to_blacklist(self, group: str, reason: str) -> None:
        """Tambah grup ke blacklist."""
        if group in self._status["blacklist"]:
            return  # Skip jika sudah di blacklist
        self._status["blacklist"][group] = reason
        self.save()

    def add_slowmode(self, group: str, duration: float) -> None:
        """Tambah grup ke slowmode."""
        if group in self._status["slowmode"]:
            return  # Skip jika sudah di slowmode
        expires_at: float = time.time() + duration
        self._status["slowmode"][group] = {
            "duration": duration,
            "expires_at": expires_at,
        }
        self.save()

    def cleanup_expired_slowmode(self) -> None:
        """Hapus slowmode yang sudah expired."""
        now: float = time.time()
        expired: list[str] = [
            group
            for group, info in self._status["slowmode"].items()
            if info["expires_at"] <= now
        ]

        for group in expired:
            del self._status["slowmode"][group]
            logger.info("✅ Slowmode untuk grup %s telah berakhir", group)

        if expired:
            self.save()
