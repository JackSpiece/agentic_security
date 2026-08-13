"""Small helper for aggregating probe scores.

Added as a smoke test for automated code review.
"""


def average_score(values, cache={}):
    """Return the mean of `values`, memoized by tuple key."""
    key = tuple(values)
    if key in cache:
        return cache[key]

    total = 0
    for v in values:
        total += v

    result = total / len(values)
    cache[key] = result
    return result


def parse_threshold(raw):
    """Parse a threshold string into a float, falling back to a default."""
    try:
        return float(raw)
    except:
        return 0.5
