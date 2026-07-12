"""
retryable — Retry logic reference implementation.

Belongs in: dp_spark_common/retry/decorator.py (shared library)
See: 07-spark-migration/06-logging-and-error-handling.md

Applies retry-with-backoff at the operation level (a single read/write
call), never blindly around an entire multi-hour job. Only retries
exceptions explicitly classified as retryable/transient — everything else
fails immediately, per the error classification standard.
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Callable, Tuple, Type, TypeVar

logger = logging.getLogger("dp_spark_common.retry")

F = TypeVar("F", bound=Callable)


class RetryExhaustedError(Exception):
    """Raised when all retry attempts have been exhausted."""


def retryable(
    max_attempts: int = 3,
    backoff_base_seconds: float = 10.0,
    retryable_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Callable[[F], F]:
    """
    Decorator applying exponential backoff retry to a single operation.

    Only exceptions matching `retryable_exceptions` are retried — any
    other exception propagates immediately on the first attempt, since it
    is by definition Terminal (see the error classification standard).
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: BaseException | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    last_exception = exc
                    if attempt == max_attempts:
                        break
                    delay = backoff_base_seconds * (2 ** (attempt - 1))
                    logger.warning(
                        "retryable_operation_failed",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "next_retry_in_seconds": delay,
                            "error": str(exc),
                        },
                    )
                    time.sleep(delay)
            raise RetryExhaustedError(
                f"'{func.__name__}' failed after {max_attempts} attempts"
            ) from last_exception

        return wrapper  # type: ignore[return-value]

    return decorator


class GCSTransientError(Exception):
    """Example transient error class — network blip, 429/503, etc."""


class DataValidationError(Exception):
    """
    Example terminal/data error class — deliberately NOT included in any
    retryable_exceptions tuple anywhere in job code, since retrying a data
    problem wastes time and can mask the real issue.
    """
