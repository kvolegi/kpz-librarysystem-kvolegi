"""
decorators.py — Decorator патерн: @timer та @log.

Додає нову поведінку до функцій динамічно.
Підтримує sync і async функції.
"""

import functools
import time
import logging
import asyncio
from typing import Any, Callable, TypeVar
from datetime import datetime

logger = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


def timer(func: F) -> F:
    """Декоратор @timer — вимірює час виконання."""
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"⏱️  [{func.__name__}] виконано за {elapsed:.4f} сек.")
            logger.info("Функція %s виконана за %.4f сек.", func.__name__, elapsed)
            return result
        return async_wrapper  # type: ignore
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"⏱️  [{func.__name__}] виконано за {elapsed:.4f} сек.")
            logger.info("Функція %s виконана за %.4f сек.", func.__name__, elapsed)
            return result
        return sync_wrapper  # type: ignore


def log(func: F) -> F:
    """Декоратор @log — логує виклик, аргументи та результат."""
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            sig = ", ".join(
                [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
            )
            print(f"📋 [{datetime.now():%H:%M:%S}] CALL {func.__name__}({sig})")
            try:
                result = await func(*args, **kwargs)
                print(f"📋 [{datetime.now():%H:%M:%S}] RETURN {func.__name__} → {result!r}")
                return result
            except Exception as e:
                print(f"📋 [{datetime.now():%H:%M:%S}] ERROR {func.__name__} → {e}")
                raise
        return async_wrapper  # type: ignore
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            sig = ", ".join(
                [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
            )
            print(f"📋 [{datetime.now():%H:%M:%S}] CALL {func.__name__}({sig})")
            try:
                result = func(*args, **kwargs)
                print(f"📋 [{datetime.now():%H:%M:%S}] RETURN {func.__name__} → {result!r}")
                return result
            except Exception as e:
                print(f"📋 [{datetime.now():%H:%M:%S}] ERROR {func.__name__} → {e}")
                raise
        return sync_wrapper  # type: ignore
