import os


class EnvError(ValueError):
    """Error saat environment variable tidak ditemukan."""

    def __init__(self, key: str) -> None:
        super().__init__(f"Environment variable {key} tidak ditemukan")


def get_env(key: str, default: str | None = None) -> str:
    """Mengambil nilai environment variable."""
    value = os.getenv(key, default)
    if value is None:
        raise EnvError(key)
    return value
