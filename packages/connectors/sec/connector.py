import time

from packages.connectors.base.models import ConnectorStatus
from packages.connectors.base.symbols import SymbolNotFoundError, normalize_symbol

from .client import SecClient
from .mapper import map_company_facts
from .models import CompanyFacts

# The SEC ticker file changes rarely; refresh it daily.
TICKER_MAP_TTL_SECONDS = 24 * 60 * 60


class SecFactsConnector:
    name = "sec_edgar"

    def __init__(self, client: SecClient, cache_ttl: int = 3600) -> None:
        self.client, self.cache_ttl = client, cache_ttl
        self._cache: dict[str, tuple[float, CompanyFacts]] = {}
        self._ciks: tuple[float, dict[str, str]] | None = None

    async def _cik(self, symbol: str) -> str:
        if not self._ciks or time.monotonic() - self._ciks[0] >= TICKER_MAP_TTL_SECONDS:
            self._ciks = (time.monotonic(), await self.client.ticker_ciks())
        cik = self._ciks[1].get(symbol)
        if not cik:
            raise SymbolNotFoundError(f"SEC has no company filings for {symbol}")
        return cik

    async def get_company_facts(self, symbol: str) -> CompanyFacts:
        symbol = normalize_symbol(symbol)
        cached = self._cache.get(symbol)
        if cached and time.monotonic() - cached[0] < self.cache_ttl:
            return cached[1]
        result = map_company_facts(await self.client.company_facts(await self._cik(symbol)), symbol)
        self._cache[symbol] = (time.monotonic(), result)
        return result

    async def health(self) -> ConnectorStatus:
        if "@" not in self.client.user_agent:
            return ConnectorStatus(name=self.name, configured=False, healthy=False,
                                   message="SEC_USER_AGENT must include a contact email")
        return ConnectorStatus(name=self.name, configured=True, healthy=True,
                               message="SEC Company Facts connector configured")
