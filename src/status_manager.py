"""Modul untuk mengelola status grup menggunakan Redis."""

import os
import time
from typing import Any, Dict, List, cast

import redis

from .config import CONFIG
from .logger import setup_logger

logger = setup_logger(__name__, CONFIG.logging["file"])


class StatusManager:
    def __init__(self) -> None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis: redis.Redis = redis.from_url(redis_url)
        self.messages_sent = 0
        self.messages_failed = 0
        logger.info("StatusManager diinisialisasi dengan Redis")

    def add_to_blacklist(self, group: str) -> None:
        """Tambahkan grup ke blacklist."""
        self.redis.sadd("blacklist", group)
        logger.info(f"Grup {group} ditambahkan ke blacklist")

    def is_blacklisted(self, group: str) -> bool:
        return bool(self.redis.sismember("blacklist", group))

    def add_to_slowmode(self, group: str, duration: int = 3600) -> None:
        expiry_time = time.time() + duration
        self.redis.zadd("slowmode", {group: expiry_time})
        logger.info(
            f"Grup {group} ditambahkan ke slowmode selama {duration} detik, berakhir pada {time.ctime(expiry_time)}"
        )

    def is_in_slowmode(self, group: str) -> bool:
        score = self.redis.zscore("slowmode", group)
        if score is None:
            return False
        if float(cast(float, score)) <= time.time():
            self.redis.zrem("slowmode", group)
            logger.info(f"Grup {group} dihapus dari slowmode karena sudah berakhir")
            return False
        return True

    def clean_expired_slowmode(self) -> None:
        self.redis.zremrangebyscore("slowmode", "-inf", time.time())
        logger.info("Membersihkan entri slowmode yang sudah berakhir")

    def get_all_status(self) -> Dict[str, Any]:
        return {
            "blacklist": list(cast(set, self.redis.smembers("blacklist"))),
            "slowmode": {
                k.decode(): float(v)
                for k, v in cast(
                    List[tuple], self.redis.zrange("slowmode", 0, -1, withscores=True)
                )
            },
        }

    def log_metrics(self) -> None:
        logger.info(
            f"Metrik kinerja: {self.messages_sent} pesan terkirim, {self.messages_failed} pesan gagal"
        )
        logger.info(
            f"Status grup: {self.redis.scard('blacklist')} dalam blacklist, {self.redis.zcard('slowmode')} dalam slowmode"
        )

    def reset_metrics(self) -> None:
        self.messages_sent = 0
        self.messages_failed = 0
