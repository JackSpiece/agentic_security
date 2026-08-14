import asyncio
import pytest
from agentic_security.probe_actor.rate_limiter import (
    AsyncTokenBucketRateLimiter,
    RateLimiterConfig,
)


@pytest.mark.asyncio
async def test_rate_limiter_immediate_acquire():
    config = RateLimiterConfig(requests_per_minute=600, max_concurrent_requests=5)
    limiter = AsyncTokenBucketRateLimiter(config=config)

    # Should acquire without blocking
    await limiter.acquire()
    limiter.release()
    assert limiter.tokens < 600.0


@pytest.mark.asyncio
async def test_rate_limiter_concurrency_limit():
    config = RateLimiterConfig(requests_per_minute=6000, max_concurrent_requests=2)
    limiter = AsyncTokenBucketRateLimiter(config=config)

    active_tasks = 0
    max_observed_active = 0

    async def worker():
        nonlocal active_tasks, max_observed_active
        await limiter.acquire()
        active_tasks += 1
        max_observed_active = max(max_observed_active, active_tasks)
        await asyncio.sleep(0.05)
        active_tasks -= 1
        limiter.release()

    await asyncio.gather(*(worker() for _ in range(5)))
    assert max_observed_active <= 2


@pytest.mark.asyncio
async def test_rate_limiter_throttle_backoff():
    config = RateLimiterConfig(initial_backoff_sec=0.1, max_backoff_sec=1.0)
    limiter = AsyncTokenBucketRateLimiter(config=config)

    backoff1 = limiter.record_throttle_event()
    assert 0.05 <= backoff1 <= 0.15

    backoff2 = limiter.record_throttle_event()
    assert backoff2 > backoff1
