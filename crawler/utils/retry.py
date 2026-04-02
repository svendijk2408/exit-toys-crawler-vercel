"""Retry decorator met exponential backoff."""

import asyncio
import functools
import logging

logger = logging.getLogger(__name__)


def retry(max_retries: int = 3, backoff_factor: float = 2.0, exceptions=(Exception,)):
    """Decorator voor async functies met exponential backoff retry."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait = backoff_factor ** attempt
                        logger.warning(
                            f"Poging {attempt + 1}/{max_retries + 1} mislukt voor "
                            f"{func.__name__}: {e}. Wacht {wait:.1f}s..."
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.error(
                            f"Alle {max_retries + 1} pogingen mislukt voor "
                            f"{func.__name__}: {e}"
                        )
            raise last_exception

        return wrapper

    return decorator
