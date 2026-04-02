"""Token bucket rate limiter voor async HTTP requests."""

import asyncio
import time


class RateLimiter:
    """Token bucket rate limiter.

    Beperkt het aantal requests per seconde door tokens bij te vullen
    met een vast tempo.
    """

    def __init__(self, rate: float = 2.0, burst: int = 3):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Wacht tot een token beschikbaar is."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1
