import json
from pathlib import Path
import time
from typing import TypedDict, cast

from .logger import get_logger

logger = get_logger(__name__)


class InvalidTypeError(TypeError):
    """Error untuk tipe data yang tidak valid."""

    def __init__(self, field: str, value: object) -> None:
        self.field = field
        self.value = value
        super().__init__(f"{field} tidak valid: {value}")


class InvalidURLError(TypeError):
    """Error untuk URL yang tidak valid."""

    def __init__(self, url: object) -> None:
        super().__init__(f"URL tidak valid: {url}")


class InvalidTimestampError(TypeError):
    """Error untuk timestamp yang tidak valid."""

    def __init__(self, timestamp: object) -> None:
        super().__init__(f"Timestamp tidak valid: {timestamp}")


class StatusDict(TypedDict):
    """Status data structure dengan type hints yang lebih ketat."""

    blacklist: dict[str, str]
    slowmode: dict[str, float]


class StatusManager:
    """Pengelola status blacklist dan slowmode."""

    def __init__(self, status_file: str = "data/status.json") -> None:
        self.status_file = Path(status_file)
        self.status: StatusDict = self._load_status()
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Memastikan direktori data ada."""
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_status(status: dict[str, dict[str, str | float]]) -> bool:
        """Validasi format status JSON."""
        required_keys = {"blacklist", "slowmode"}
        return (
            all(key in status for key in required_keys)
            and isinstance(status["blacklist"], dict)
            and isinstance(status["slowmode"], dict)
        )

    def _load_status(self) -> StatusDict:
        """Memuat status dari file JSON."""
        default_status: StatusDict = {"blacklist": {}, "slowmode": {}}

        if not self.status_file.exists():
            return default_status

        try:
            content = self.status_file.read_text(encoding="utf-8")
            loaded_status = json.loads(content)
            if not self._validate_status(loaded_status):
                logger.error("Format status.json tidak valid")
                return default_status
        except Exception as e:
            logger.error("Error membaca status: %s", str(e))
            return default_status
        else:
            return cast(StatusDict, loaded_status)

    def save(self) -> None:
        """Menyimpan status ke file dengan penanganan error."""
        try:
            self.status_file.write_text(
                json.dumps(self.status, indent=2), encoding="utf-8"
            )
        except Exception as e:
            logger.error("Error menyimpan status: %s", str(e))

    @staticmethod
    def _validate_entry(key: object, value: object) -> tuple[str, float]:
        """Validasi satu entry slowmode.

        Args:
            key: Key yang akan divalidasi
            value: Value yang akan divalidasi

        Returns:
            tuple[str, float]: Tuple berisi (key, value) yang sudah divalidasi

        Raises:
            InvalidURLError: Jika key bukan string
            InvalidTimestampError: Jika value bukan int/float
        """
        if not isinstance(key, str):
            raise InvalidURLError(key)

        if not isinstance(value, int | float):
            raise InvalidTimestampError(value)

        return key, float(value)

    def clean_expired_slowmode(self) -> None:
        """Membersihkan slowmode dengan validasi tipe yang lebih ketat."""
        current_time = time.time()
        cleaned_slowmode: dict[str, float] = {}

        # Ambil dan validasi slowmode
        slowmode = self.status.get("slowmode")
        if not isinstance(slowmode, dict):
            logger.error("Format slowmode tidak valid")
            self.status["slowmode"] = cleaned_slowmode
            self.save()
            return

        # Proses setiap entry
        for key, value in slowmode.items():
            try:
                # Menggunakan static method
                validated_key, validated_time = self._validate_entry(key, value)
                if validated_time > current_time:
                    cleaned_slowmode[validated_key] = validated_time

            except TypeError as e:
                logger.warning(str(e))
                continue

        # Update status jika ada perubahan
        if self.status["slowmode"] != cleaned_slowmode:
            self.status["slowmode"] = cleaned_slowmode
            self.save()

    def add_blacklist(self, url: str, reason: str) -> None:
        """Menambahkan grup ke blacklist."""
        if isinstance(self.status["blacklist"], dict):
            self.status["blacklist"][url] = reason
            self.save()

    def add_slowmode(self, url: str, duration: int) -> None:
        """Menambahkan grup ke slowmode."""
        expire_time = time.time() + duration
        if isinstance(self.status["slowmode"], dict):
            self.status["slowmode"][url] = expire_time
            self.save()

    @staticmethod
    def get_all_groups() -> list[str]:
        """Mendapatkan daftar grup dengan error handling yang lebih baik."""
        groups: list[str] = []
        try:
            groups_file = Path("data/groups.txt")
            if not groups_file.exists():
                logger.error("File groups.txt tidak ditemukan")
                return groups

            content = groups_file.read_text(encoding="utf-8")

            # Validasi format setiap baris
            for line_num, raw_line in enumerate(content.splitlines(), 1):
                cleaned_line = raw_line.strip()
                if not cleaned_line:
                    continue

                if not cleaned_line.startswith(("https://t.me/", "t.me/")):
                    logger.warning(
                        "Baris %d: Format URL tidak valid: %s", line_num, cleaned_line
                    )
                    continue

                groups.append(cleaned_line)

        except Exception as e:
            logger.error(
                "Error saat membaca groups.txt: %s - %s", type(e).__name__, str(e)
            )

        return groups

    def get_active_groups(self) -> list[str]:
        """Mendapatkan daftar grup yang aktif."""
        self.clean_expired_slowmode()

        try:
            groups = self.get_all_groups()
        except Exception as e:
            logger.error("Error membaca groups.txt: %s", str(e))
            return []

        return [
            group
            for group in groups
            if group not in self.status["blacklist"]
            and group not in self.status["slowmode"]
        ]
