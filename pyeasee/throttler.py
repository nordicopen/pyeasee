"""
Throttler for API calls
"""
import asyncio
from collections import deque
import logging
import time
from typing import Deque

_LOGGER = logging.getLogger(__name__)


class Throttler:
    def __init__(self, rate_limit: int, period: float = 1.0, name: str = ""):
        self.rate_limit = rate_limit
        self.period = period
        self.name = name

        self._task_logs: Deque[float] = deque()

    def flush(self):
        now = time.monotonic()
        while self._task_logs:
            if now - self._task_logs[0] > self.period:
                self._task_logs.popleft()
            else:
                break

    async def acquire(self):
        self.flush()
        if len(self._task_logs) >= self.rate_limit:
            _LOGGER.debug(
                "Delay %f seconds due to throttling (%d calls per %f seconds allowed for %s).",
                self.period / self.rate_limit,
                self.rate_limit,
                self.period,
                self.name,
            )
            await asyncio.sleep(self.period / self.rate_limit)

        self._task_logs.append(time.monotonic())

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc, tb):
        pass
