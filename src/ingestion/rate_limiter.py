import asyncio
import time
import logging
from collections import deque

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float = 60.0):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._calls: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            while self._calls and now - self._calls[0] > self.period_seconds:
                self._calls.popleft()

            if len(self._calls) >= self.max_calls:
                wait = self.period_seconds - (now - self._calls[0]) + 0.1
                logger.info(f"Rate limit reached, waiting {wait:.1f}s")
                await asyncio.sleep(wait)
                now = time.monotonic()
                while self._calls and now - self._calls[0] > self.period_seconds:
                    self._calls.popleft()

            self._calls.append(now)


api_football_limiter = RateLimiter(max_calls=10, period_seconds=60.0)