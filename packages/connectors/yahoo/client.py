import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

import yfinance as yf
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from .exceptions import YahooConnectorError, YahooTimeoutError

T = TypeVar("T")


class YahooClient:
    def __init__(self, timeout: float = 10, retries: int = 2) -> None:
        self.timeout = timeout
        self.retries = retries

    async def _call(self, operation: Callable[[], T]) -> T:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self.retries + 1), wait=wait_exponential(max=2),
                retry=retry_if_exception_type((TimeoutError, ConnectionError)), reraise=True,
            ):
                with attempt:
                    return await asyncio.wait_for(asyncio.to_thread(operation), timeout=self.timeout)
        except (TimeoutError, asyncio.TimeoutError) as exc:
            raise YahooTimeoutError("Yahoo Finance request timed out") from exc
        except Exception as exc:
            raise YahooConnectorError(f"Yahoo Finance request failed: {type(exc).__name__}") from exc
        raise YahooConnectorError("Yahoo Finance request failed")

    async def info(self, symbol: str) -> dict[str, Any]:
        return await self._call(lambda: yf.Ticker(symbol).info)

    async def history(self, symbol: str, period: str) -> Any:
        return await self._call(lambda: yf.Ticker(symbol).history(period=period, auto_adjust=False))

    async def options(self, symbol: str) -> tuple[str, ...]:
        return await self._call(lambda: yf.Ticker(symbol).options)

    async def option_chain(self, symbol: str, expiration: str) -> Any:
        return await self._call(lambda: yf.Ticker(symbol).option_chain(expiration))

