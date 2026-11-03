import logging
import time
from datetime import datetime, timezone
from typing import Any

from packages.connectors.base.connector import MarketDataConnector
from packages.connectors.base.models import (
    CompanyProfile,
    ConnectorStatus,
    OptionChain,
    OptionExpirations,
    PriceHistory,
    Quote,
)
from packages.connectors.base.symbols import SymbolNotFoundError, normalize_symbol

from .client import YahooClient
from .mapper import contracts, freshness, price_bars, timestamp

logger = logging.getLogger(__name__)


class YahooMarketDataConnector(MarketDataConnector):
    provider = "yahoo_finance"

    def __init__(self, client: YahooClient, cache_ttl: int = 30) -> None:
        self.client, self.cache_ttl = client, cache_ttl
        self._cache: dict[str, tuple[float, Any]] = {}

    def _validate(self, symbol: str) -> str:
        return normalize_symbol(symbol)

    async def _info(self, symbol: str) -> dict[str, Any]:
        info: dict[str, Any] = await self._cached(f"info:{symbol}", lambda: self.client.info(symbol))
        # yfinance returns a near-empty dict (no quoteType, no name, no price) for unknown symbols.
        if info and not any(info.get(key) for key in ("quoteType", "longName", "shortName",
                                                      "regularMarketPrice", "currentPrice")):
            raise SymbolNotFoundError(f"Yahoo Finance has no listing for {symbol}")
        return info

    async def _cached(self, key: str, loader: Any) -> Any:
        item = self._cache.get(key)
        if item and time.monotonic() - item[0] < self.cache_ttl:
            return item[1]
        value = await loader()
        self._cache[key] = (time.monotonic(), value)
        return value

    def _meta(self, as_of: datetime | None, warnings: list[str]) -> dict[str, Any]:
        return {"provider": self.provider, "as_of": as_of, "retrieved_at": datetime.now(timezone.utc),
                "freshness": freshness(as_of), "warnings": warnings}

    async def get_quote(self, symbol: str) -> Quote:
        symbol = self._validate(symbol)
        info = await self._info(symbol)
        as_of = timestamp(info.get("regularMarketTime"))
        price = info.get("currentPrice", info.get("regularMarketPrice"))
        warnings = ["Latest price is unavailable"] if price is None else []
        return Quote(**self._meta(as_of, warnings), symbol=symbol, price=price,
                     change=info.get("regularMarketChange"),
                     change_percent=info.get("regularMarketChangePercent"),
                     volume=info.get("regularMarketVolume"), market_cap=info.get("marketCap"))

    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        symbol = self._validate(symbol)
        info = await self._info(symbol)
        as_of = timestamp(info.get("regularMarketTime"))
        return CompanyProfile(**self._meta(as_of, []), symbol=symbol,
                              company_name=info.get("longName") or info.get("shortName"),
                              market_cap=info.get("marketCap"),
                              fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
                              fifty_two_week_low=info.get("fiftyTwoWeekLow"),
                              average_volume=info.get("averageVolume"))

    async def get_price_history(self, symbol: str, period: str) -> PriceHistory:
        symbol = self._validate(symbol)
        if period not in {"1mo", "3mo", "6mo", "1y"}:
            raise ValueError("Unsupported history period")
        await self._info(symbol)
        frame = await self._cached(f"history:{symbol}:{period}",
                                   lambda: self.client.history(symbol, period))
        bars = price_bars(frame)
        as_of = bars[-1].timestamp if bars else None
        warnings = ["No historical prices returned"] if not bars else []
        return PriceHistory(**self._meta(as_of, warnings), symbol=symbol, period=period, bars=bars)

    async def get_option_expirations(self, symbol: str) -> OptionExpirations:
        symbol = self._validate(symbol)
        await self._info(symbol)
        values = await self._cached(f"options:{symbol}", lambda: self.client.options(symbol))
        warnings = ["No option expirations returned"] if not values else []
        return OptionExpirations(**self._meta(datetime.now(timezone.utc), warnings),
                                 symbol=symbol, expirations=list(values))

    async def get_option_chain(self, symbol: str, expiration: str) -> OptionChain:
        symbol = self._validate(symbol)
        chain = await self._cached(f"chain:{symbol}:{expiration}",
                                   lambda: self.client.option_chain(symbol, expiration))
        calls, puts = contracts(chain.calls), contracts(chain.puts)
        return OptionChain(**self._meta(datetime.now(timezone.utc), []), symbol=symbol,
                           expiration=expiration, calls=calls, puts=puts)

    async def health(self) -> ConnectorStatus:
        try:
            await self.get_quote("SPY")
            return ConnectorStatus(name=self.provider, configured=True, healthy=True,
                                   message="Yahoo Finance responded")
        except Exception as exc:
            logger.warning("connector_health_failed", extra={"error_type": type(exc).__name__})
            return ConnectorStatus(name=self.provider, configured=True, healthy=False,
                                   message=f"Yahoo Finance unavailable: {type(exc).__name__}")

