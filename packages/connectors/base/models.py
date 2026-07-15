from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Freshness(StrEnum):
    LIVE_OR_RECENT = "live_or_recent"
    DELAYED = "delayed"
    STALE = "stale"
    UNAVAILABLE = "unavailable"


class ConnectorMetadata(BaseModel):
    model_config = ConfigDict(alias_generator=lambda value: "".join(
        word if index == 0 else word.title() for index, word in enumerate(value.split("_"))
    ), populate_by_name=True)
    provider: str
    as_of: datetime | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    freshness: Freshness = Freshness.UNAVAILABLE
    warnings: list[str] = Field(default_factory=list)


class Quote(ConnectorMetadata):
    symbol: str
    price: float | None = None
    change: float | None = None
    change_percent: float | None = None
    volume: int | None = None
    market_cap: int | None = None


class CompanyProfile(ConnectorMetadata):
    symbol: str
    company_name: str | None = None
    market_cap: int | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    average_volume: int | None = None


class PriceBar(BaseModel):
    timestamp: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = None


class PriceHistory(ConnectorMetadata):
    symbol: str
    period: str
    bars: list[PriceBar]


class OptionContract(BaseModel):
    contract_symbol: str
    strike: float
    last_price: float | None = None
    volume: int | None = None
    open_interest: int | None = None
    implied_volatility: float | None = None


class OptionChain(ConnectorMetadata):
    symbol: str
    expiration: str
    calls: list[OptionContract]
    puts: list[OptionContract]


class OptionExpirations(ConnectorMetadata):
    symbol: str
    expirations: list[str]


class ConnectorStatus(BaseModel):
    name: str
    configured: bool
    healthy: bool
    message: str
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

