"""Modul untuk mengelola status.json."""

import json
import time
from pathlib import Path
from typing import Final, cast

from .config import DATA_DIR, GROUPS_FILE, MESSAGES_DIR
from .custom_types import SlowmodeInfo, StatusData, StatusManagerProtocol
from .exceptions import StatusError
from .logger import (
    BLACKLIST_EMOJI,
    INFO_EMOJI,
    WARNING_EMOJI,
    setup_logger,
)

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


def _raise_status_error(error: str, original_error: Exception | None = None) -> None:
    """Raise status error."""
    if original_error:
        raise StatusError(error) from original_error
    raise StatusError(error) from None


class StatusManager(StatusManagerProtocol):
    """Class untuk mengelola status.json."""

    def __init__(self) -> None:
        """Inisialisasi status manager."""
        # Pastikan folder data ada dan bisa ditulis
        DATA_DIR.mkdir(exist_ok=True)
        MESSAGES_DIR.mkdir(exist_ok=True)
        self._status: StatusData = cast(StatusData, DEFAULT_STATUS.copy())
        self._groups: set[str] = set()
        self._load_status()
        self._load_groups()

    def _load_status(self) -> None:
        """Load status dari file."""
        try:
            if not STATUS_FILE.exists():
                logger.info(f"{INFO_EMOJI} File status belum ada, membuat baru")
                self.save()
                return

            try:
                data = json.loads(STATUS_FILE.read_text())
            except json.JSONDecodeError:
                logger.warning(f"{WARNING_EMOJI} File status corrupt, membuat baru")
                self._status = cast(StatusData, DEFAULT_STATUS.copy())
                self.save()
                return

            # Validasi dan merge dengan existing blacklist
            existing_blacklist = self._status.get("blacklist", {})
            new_blacklist = data.get("blacklist", {})
            merged_blacklist = {**existing_blacklist, **new_blacklist}

            self._status = cast(
                StatusData,
                {
                    "blacklist": merged_blacklist,
                    "slowmode": data.get("slowmode", {}),
                    "last_updated": data.get("last_updated", time.time()),
                },
            )

        except Exception:
            logger.exception("Error saat load status")
            self._status = cast(StatusData, DEFAULT_STATUS.copy())
            self.save()

    def _load_groups(self) -> None:
        """Load daftar grup dari file."""
        try:
            if not GROUPS_FILE.exists():
                _raise_status_error(StatusError.MISSING_GROUPS)

            # Load groups apa adanya, tanpa modifikasi atau validasi
            groups = GROUPS_FILE.read_text().strip().splitlines()
            self._groups = set(filter(None, groups))  # Filter empty lines saja

            logger.info("✅ Berhasil load %d grup", len(self._groups))

        except Exception as e:
            logger.exception("Error saat load groups")
            _raise_status_error(StatusError.LOAD_GROUPS_ERROR.format(str(e)), e)

    def get_groups(self) -> set[str]:
        """Get list grup."""
        return self._groups.copy()

    def get_blacklist(self) -> dict[str, str]:
        """Get dict blacklist."""
        return dict(self._status["blacklist"])

    def get_slowmode(self) -> dict[str, SlowmodeInfo]:
        """Get dict slowmode."""
        return cast(
            dict[str, SlowmodeInfo],
            {k: dict(v) for k, v in self._status["slowmode"].items()},
        )

    def get_slowmode_info(self, group: str) -> SlowmodeInfo | None:
        """Get info slowmode untuk grup."""
        if group not in self._status["slowmode"]:
            return None
        return cast(SlowmodeInfo, dict(self._status["slowmode"][group]))

    def get_active_groups(self) -> set[str]:
        """Get grup yang aktif (non-blacklist & non-slowmode)."""
        current_time = time.time()
        return {
            group
            for group in self._groups
            if group not in self._status["blacklist"]
            and not (
                group in self._status["slowmode"]
                and current_time < self._status["slowmode"][group]["expires_at"]
            )
        }

    def add_to_blacklist(self, group: str, reason: str) -> None:
        """Tambah grup ke blacklist."""
        group_lower = group.lower()
        if not any(g.lower() == group_lower for g in self._status["blacklist"]):
            self._status["blacklist"][group] = reason
            self._groups.discard(group)

    def add_slowmode(self, group: str, duration: float) -> None:
        """Tambah grup ke slowmode.

        Args:
            group: Link grup Telegram
            duration: Durasi slowmode dalam detik
        """
        expires_at = time.time() + duration
        self._status["slowmode"][group] = {
            "duration": duration,
            "expires_at": expires_at,
        }
        self.save()

    def cleanup_expired_slowmode(self) -> None:
        """Cleanup slowmode yang sudah expired."""
        now = time.time()
        expired = []

        for group, info in self._status["slowmode"].items():
            if info["expires_at"] < now:
                expired.append(group)

        if expired:
            for group in expired:
                del self._status["slowmode"][group]

            if len(expired) == 1:
                logger.info(f"💡 Slowmode expired dihapus: {expired[0]}")
            else:
                logger.info(
                    f"💡 {len(expired)} slowmode expired dihapus: "
                    f"{', '.join(expired)}"
                )

    def cleanup_status(self) -> None:
        """Cleanup status yang tidak valid."""
        self.cleanup_expired_slowmode()

    def save(self) -> None:
        """Save status ke file."""
        try:
            self._status["last_updated"] = time.time()
            json_data = json.dumps(self._status, indent=2)
            STATUS_FILE.write_text(json_data)
        except Exception as e:
            logger.exception("Error saat save status")
            _raise_status_error(StatusError.SAVE_ERROR.format(str(e)), e)

    def _save_groups(self) -> None:
        """Save daftar grup ke file."""
        try:
            # Pertahankan format asli, hanya hapus yang invalid
            groups = sorted(self._groups)
            if groups:  # Hanya write jika ada grup
                GROUPS_FILE.write_text("\n".join(groups) + "\n")
        except Exception as e:
            logger.exception("Error saat save groups")
            _raise_status_error(StatusError.SAVE_ERROR.format(str(e)), e)

    def _log_invalid_groups(
        self, invalid_groups: dict[str, list[str] | dict[str, str]]
    ) -> None:
        """Log grup yang tidak valid."""
        # Log format errors first
        format_list = invalid_groups.get("format", [])
        if isinstance(format_list, list) and format_list:
            logger.warning(
                f"{WARNING_EMOJI} Format tidak valid ({len(format_list)} grup):"
            )
            for group in format_list:
                logger.warning(f"  • {group}")

        # Group blacklisted items by error type
        blacklist_dict = invalid_groups.get("blacklist", {})
        if isinstance(blacklist_dict, dict) and blacklist_dict:
            # Create error type groups
            error_groups: dict[str, list[str]] = {}
            for group, reason in blacklist_dict.items():
                if reason not in error_groups:
                    error_groups[reason] = []
                error_groups[reason].append(group)

            # Log total blacklisted first
            logger.warning(
                f"{BLACKLIST_EMOJI} Total blacklisted: {len(blacklist_dict)} grup\n"
            )

            # Log each error type group
            for error_type, groups in error_groups.items():
                logger.warning(f"{error_type} ({len(groups)} grup):")
                for group in groups:
                    logger.warning(f"  • {group}")
                # Add newline between groups for better readability
                logger.warning("")

    def is_slowmode_active(self, group: str) -> bool:
        """Check apakah grup dalam slowmode."""
        if group not in self._status["slowmode"]:
            return False
        expires_at = float(self._status["slowmode"][group]["expires_at"])
        return time.time() < expires_at

    def _log_statistics(self) -> None:
        """Log statistik status."""
        total = len(self._groups) + len(self._status["blacklist"])  # Total semua grup
        if total == 0:
            return

        blacklist = len(self._status["blacklist"])
        slowmode = len(self._status["slowmode"])
        active = len(self.get_active_groups())

        logger.info(
            f"📊 Status: {total} grup | "
            f"✅ {active} aktif | "
            f"⛔ {blacklist} blacklist | "
            f"⏳ {slowmode} slowmode"
        )
