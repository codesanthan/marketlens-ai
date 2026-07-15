from datetime import datetime, timedelta, timezone

from packages.connectors.base.connector import MarketDataConnector
from packages.connectors.base.models import (
    CompanyProfile,
    ConnectorStatus,
    Freshness,
    OptionChain,
    OptionContract,
    OptionExpirations,
    PriceBar,
    PriceHistory,
    Quote,
)

SYMBOLS = ("SPY", "QQQ", "NVDA", "AAPL", "MSFT", "AMZN", "META", "TSLA")
PRICES = {symbol: 100.0 + index * 37.5 for index, symbol in enumerate(SYMBOLS)}


class MockMarketDataConnector(MarketDataConnector):
    provider = "mock"

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    async def get_quote(self, symbol: str) -> Quote:
        now, price = self._now(), PRICES[symbol]
        return Quote(provider=self.provider, as_of=now, freshness=Freshness.LIVE_OR_RECENT,
                     symbol=symbol, price=price, change=1.25, change_percent=0.5,
                     volume=1_250_000, market_cap=2_000_000_000)

    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        now, price = self._now(), PRICES[symbol]
        return CompanyProfile(provider=self.provider, as_of=now, freshness=Freshness.LIVE_OR_RECENT,
                              symbol=symbol, company_name=f"{symbol} Mock Company",
                              market_cap=2_000_000_000, fifty_two_week_high=price * 1.2,
                              fifty_two_week_low=price * .7, average_volume=1_000_000)

    async def get_price_history(self, symbol: str, period: str) -> PriceHistory:
        now, price = self._now(), PRICES[symbol]
        bars = [PriceBar(timestamp=now - timedelta(days=29-i), open=price+i, high=price+i+2,
                         low=price+i-2, close=price+i+1, volume=1_000_000+i*1_000)
                for i in range(30)]
        return PriceHistory(provider=self.provider, as_of=now, freshness=Freshness.LIVE_OR_RECENT,
                            symbol=symbol, period=period, bars=bars)

    async def get_option_expirations(self, symbol: str) -> OptionExpirations:
        now = self._now()
        return OptionExpirations(provider=self.provider, as_of=now,
                                 freshness=Freshness.LIVE_OR_RECENT, symbol=symbol,
                                 expirations=[(now + timedelta(days=30)).date().isoformat()])

    async def get_option_chain(self, symbol: str, expiration: str) -> OptionChain:
        now, price = self._now(), PRICES[symbol]
        contract = OptionContract(contract_symbol=f"{symbol}MOCK", strike=price,
                                  last_price=5, volume=200, open_interest=500,
                                  implied_volatility=.25)
        return OptionChain(provider=self.provider, as_of=now, freshness=Freshness.LIVE_OR_RECENT,
                           symbol=symbol, expiration=expiration, calls=[contract], puts=[contract])

    async def health(self) -> ConnectorStatus:
        return ConnectorStatus(name=self.provider, configured=True, healthy=True,
                               message="Deterministic mock connector ready")

