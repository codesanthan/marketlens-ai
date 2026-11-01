import time

from packages.connectors.base.models import ConnectorStatus

from .client import SecClient
from .mapper import map_company_facts
from .models import CompanyFacts

CIKS = {"SPY": "0000884394", "QQQ": "0001067839", "NVDA": "0001045810",
        "AAPL": "0000320193", "MSFT": "0000789019", "AMZN": "0001018724",
        "META": "0001326801", "TSLA": "0001318605"}


class SecFactsConnector:
    name = "sec_edgar"

    def __init__(self, client: SecClient, cache_ttl: int = 3600) -> None:
        self.client, self.cache_ttl = client, cache_ttl
        self._cache: dict[str, tuple[float, CompanyFacts]] = {}

    async def get_company_facts(self, symbol: str) -> CompanyFacts:
        symbol = symbol.strip().upper()
        if symbol not in CIKS:
            raise ValueError(f"Unsupported symbol: {symbol}")
        cached = self._cache.get(symbol)
        if cached and time.monotonic() - cached[0] < self.cache_ttl:
            return cached[1]
        result = map_company_facts(await self.client.company_facts(CIKS[symbol]), symbol)
        self._cache[symbol] = (time.monotonic(), result)
        return result

    async def health(self) -> ConnectorStatus:
        if "@" not in self.client.user_agent:
            return ConnectorStatus(name=self.name, configured=False, healthy=False,
                                   message="SEC_USER_AGENT must include a contact email")
        return ConnectorStatus(name=self.name, configured=True, healthy=True,
                               message="SEC Company Facts connector configured")
