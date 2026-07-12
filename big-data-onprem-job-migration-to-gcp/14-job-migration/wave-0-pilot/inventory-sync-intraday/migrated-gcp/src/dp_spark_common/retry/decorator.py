"""
retryable — see 07-spark-migration/06-logging-and-error-handling.md
and 07-spark-migration/examples/retry_decorator.py (canonical source).
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Callable, Tuple, Type, TypeVar

logger = logging.getLogger("dp_spark_common.retry")

F = TypeVar("F", bound=Callable)


class RetryExhaustedError(Exception):
    pass


def retryable(
    max_attempts: int = 3,
    backoff_base_seconds: float = 10.0,
    retryable_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Callable[[F], F]:
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
            raise RetryExhaustedError(f"'{func.__name__}' failed after {max_attempts} attempts") from last_exception

        return wrapper  # type: ignore[return-value]

    return decorator


class GCSTransientError(Exception):
    pass


class DataValidationError(Exception):
    pass
