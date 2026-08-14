import asyncio
import pytest
from agentic_security.probe_actor.async_poller import poll_with_timeout


@pytest.mark.asyncio
async def test_poll_with_timeout_success():
    async def sample_coro():
        await asyncio.sleep(0.01)
        return "success"

    result = await poll_with_timeout(sample_coro, timeout=1.0)
    assert result == "success"


@pytest.mark.asyncio
async def test_poll_with_timeout_expired():
    async def slow_coro():
        await asyncio.sleep(0.5)
        return "done"

    result = await poll_with_timeout(slow_coro, timeout=0.05)
    assert result is None
