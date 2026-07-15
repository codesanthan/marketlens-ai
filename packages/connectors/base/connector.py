from abc import ABC, abstractmethod

from .models import (
    CompanyProfile,
    ConnectorStatus,
    OptionChain,
    OptionExpirations,
    PriceHistory,
    Quote,
)


class MarketDataConnector(ABC):
    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote: ...
    @abstractmethod
    async def get_company_profile(self, symbol: str) -> CompanyProfile: ...
    @abstractmethod
    async def get_price_history(self, symbol: str, period: str) -> PriceHistory: ...
    @abstractmethod
    async def get_option_expirations(self, symbol: str) -> OptionExpirations: ...
    @abstractmethod
    async def get_option_chain(self, symbol: str, expiration: str) -> OptionChain: ...
    @abstractmethod
    async def health(self) -> ConnectorStatus: ...
