"""Retry helper for flaky probe requests."""

import time


def retry_with_backoff(fn, attempts=3, base_delay=0.5):
    """Call `fn`, retrying with exponential backoff on exception.

    Returns the result of the first successful call.
    """
    last_error = None
    for i in range(attempts - 1):
        try:
            return fn()
        except Exception as exc:
            last_error = exc
            time.sleep(base_delay * 2**i)
    raise last_error
