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
async def test_rate_limiter_cancellation_safety():
    """Verify that cancelling a waiting acquire() does not leak semaphore permits."""
    config = RateLimiterConfig(
        requests_per_minute=1, max_concurrent_requests=1
    )  # only 1 permit
    limiter = AsyncTokenBucketRateLimiter(config=config)
    limiter.tokens = 0.0  # Force waiting inside acquire()

    task = asyncio.create_task(limiter.acquire())
    await asyncio.sleep(0.01)  # Let it enter sleep
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    # Permit should not be leaked; next acquire should be able to acquire lock
    limiter.tokens = 5.0
    await asyncio.wait_for(limiter.acquire(), timeout=0.5)
    limiter.release()


@pytest.mark.asyncio
async def test_rate_limiter_escalation_across_retries():
    """Verify backoff multiplies properly even when acquire() runs between throttle events."""
    config = RateLimiterConfig(
        initial_backoff_sec=0.05, max_backoff_sec=1.0, backoff_factor=2.0
    )
    limiter = AsyncTokenBucketRateLimiter(config=config)

    # First throttle event
    d1 = limiter.record_throttle_event()
    assert limiter._current_backoff == 0.05

    # Simulate caller acquiring and retrying
    await limiter.acquire()
    limiter.release()

    # Second throttle event should escalate (0.05 * 2.0 = 0.10)
    d2 = limiter.record_throttle_event()
    assert limiter._current_backoff == 0.10

    # Reset on success
    limiter.reset_backoff()
    assert limiter._current_backoff == 0.0
