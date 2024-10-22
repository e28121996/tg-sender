"""Module for scheduling message sending tasks."""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Any, Callable, Tuple

from .config import CONFIG
from .logger import setup_logger

logger = setup_logger(__name__, CONFIG.logging["file"])


class Scheduler:
    """Class for scheduling message sending tasks."""

    def __init__(self) -> None:
        """Initialize the Scheduler."""
        self.task: Callable[..., Any] = lambda: None
        self.args: Tuple[Any, ...] = ()
        self.min_interval = CONFIG.interval["min"]
        self.max_interval = CONFIG.interval["max"]
        logger.info("Scheduler diinisialisasi")

    def set_task(self, task: Callable[..., Any], *args: Any) -> None:
        """Set the task and arguments for the scheduler."""
        self.task = task
        self.args = args
        logger.info("Task dijadwalkan dalam Scheduler")

    async def run(self) -> None:
        """Run the scheduler."""
        while True:
            logger.info("Memulai task terjadwal")
            await self.task(*self.args)
            next_run = self._calculate_next_run()
            logger.info(
                f"Task selesai. Jadwal berikutnya: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            wait_time = (next_run - datetime.now()).total_seconds()
            logger.info(f"Menunggu {wait_time:.2f} detik sampai jadwal berikutnya")
            await asyncio.sleep(wait_time)

    def _calculate_next_run(self) -> datetime:
        """Calculate the next run time."""
        interval = random.uniform(self.min_interval, self.max_interval)
        return datetime.now() + timedelta(hours=interval)
