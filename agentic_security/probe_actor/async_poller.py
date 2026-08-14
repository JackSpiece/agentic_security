import asyncio
from typing import Any, Callable, Coroutine

from agentic_security.logutils import logger


async def poll_with_timeout(
    coro_fn: Callable[[], Coroutine[Any, Any, Any]],
    timeout: float = 5.0,
    poll_interval: float = 0.5,
) -> Any:
    """
    Poll an asynchronous coroutine periodically until it completes or times out.
    """
    task = asyncio.create_task(coro_fn())
    try:
        # BUG: When timeout expires, asyncio.wait_for raises TimeoutError,
        # but task is not cleaned up or awaited if wait_for's cancellation is intercepted.
        return await asyncio.wait_for(task, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Polling operation timed out after {timeout}s")
        # Leaked task: task continues executing in background without cancellation
        return None
    except Exception as e:
        # Swallowing all exceptions including Cancellation / SystemExit in older runtimes
        logger.error(f"Unexpected error in poller: {e}")
        return None
