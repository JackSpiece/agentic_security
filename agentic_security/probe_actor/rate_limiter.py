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
        self._backoff_until = 0.0

    async def acquire(self) -> None:
        """Acquire permission to dispatch a request, safely releasing semaphore on cancellation."""
        await self._semaphore.acquire()
        try:
            async with self._lock:
                while True:
                    now = time.monotonic()

                    # Wait for active backoff window if throttled
                    if now < self._backoff_until:
                        wait_backoff = self._backoff_until - now
                        await asyncio.sleep(wait_backoff)
                        continue

                    elapsed = now - self.last_update
                    self.last_update = now
                    self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)

                    if self.tokens >= 1.0:
                        self.tokens -= 1.0
                        break

                    wait_time = (1.0 - self.tokens) / self.fill_rate
                    await asyncio.sleep(wait_time)
        except BaseException:
            self._semaphore.release()
            raise

    def release(self) -> None:
        """Release the concurrency slot."""
        self._semaphore.release()

    def record_throttle_event(self) -> float:
        """
        Record a 429 Too Many Requests or 503 Service Unavailable event
        and escalate backoff with jitter.
        """
        if self._current_backoff <= 0:
            next_backoff = self.config.initial_backoff_sec
        else:
            next_backoff = min(
                self.config.max_backoff_sec,
                self._current_backoff * self.config.backoff_factor,
            )

        self._current_backoff = next_backoff
        jitter = random.uniform(-self.config.jitter_range, self.config.jitter_range)
        duration = max(0.1, next_backoff * (1.0 + jitter))
        self._backoff_until = time.monotonic() + duration
        logger.warning(
            f"Rate limiter throttled: backing off for {duration:.2f}s (base: {next_backoff:.2f}s)"
        )
        return duration

    def reset_backoff(self) -> None:
        """Reset backoff escalation upon successful request completion."""
        self._current_backoff = 0.0
        self._backoff_until = 0.0
