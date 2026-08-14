import asyncio
import random
import time
from dataclasses import dataclass
from typing import Optional

from agentic_security.logutils import logger


@dataclass
class RateLimiterConfig:
    requests_per_minute: int = 60
    max_concurrent_requests: int = 10
    initial_backoff_sec: float = 1.0
    max_backoff_sec: float = 30.0
    backoff_factor: float = 2.0
    jitter_range: float = 0.2


class AsyncTokenBucketRateLimiter:
    """
    Asynchronous token-bucket rate limiter with concurrency limits
    and adaptive backoff for LLM probing.
    """

    def __init__(self, config: Optional[RateLimiterConfig] = None):
        self.config = config or RateLimiterConfig()
        self.capacity = float(self.config.requests_per_minute)
        self.tokens = float(self.config.requests_per_minute)
        self.fill_rate = float(self.config.requests_per_minute) / 60.0
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        self._current_backoff = 0.0

    async def acquire(self) -> None:
        """Acquire permission to dispatch a request, waiting if rate limits are reached."""
        await self._semaphore.acquire()
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.last_update = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)

                if self._current_backoff > 0:
                    sleep_time = self._current_backoff
                    self._current_backoff = 0.0
                    await asyncio.sleep(sleep_time)
                    continue

                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    break

                wait_time = (1.0 - self.tokens) / self.fill_rate
                await asyncio.sleep(wait_time)

    def release(self) -> None:
        """Release the concurrency slot."""
        self._semaphore.release()

    def record_throttle_event(self) -> float:
        """
        Record a 429 Too Many Requests or 503 Service Unavailable event
        and compute adaptive backoff with jitter.
        """
        if self._current_backoff <= 0:
            next_backoff = self.config.initial_backoff_sec
        else:
            next_backoff = min(
                self.config.max_backoff_sec,
                self._current_backoff * self.config.backoff_factor,
            )

        jitter = random.uniform(-self.config.jitter_range, self.config.jitter_range)
        self._current_backoff = max(0.1, next_backoff * (1.0 + jitter))
        logger.warning(
            f"Rate limiter throttled: backing off for {self._current_backoff:.2f}s"
        )
        return self._current_backoff
