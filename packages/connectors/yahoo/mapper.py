from datetime import datetime, timezone
from typing import Any

from packages.connectors.base.models import Freshness, OptionContract, PriceBar


def freshness(as_of: datetime | None, now: datetime | None = None) -> Freshness:
    if as_of is None:
        return Freshness.UNAVAILABLE
    age = (now or datetime.now(timezone.utc)) - as_of.astimezone(timezone.utc)
    if age.total_seconds() <= 20 * 60:
        return Freshness.LIVE_OR_RECENT
    if age.total_seconds() <= 24 * 3600:
        return Freshness.DELAYED
    return Freshness.STALE


def timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def price_bars(frame: Any) -> list[PriceBar]:
    result = []
    for index, row in frame.iterrows():
        ts = index.to_pydatetime() if hasattr(index, "to_pydatetime") else index
        result.append(PriceBar(timestamp=timestamp(ts) or datetime.now(timezone.utc),
                               open=_number(row.get("Open")), high=_number(row.get("High")),
                               low=_number(row.get("Low")), close=_number(row.get("Close")),
                               volume=_integer(row.get("Volume"))))
    return result


def contracts(frame: Any) -> list[OptionContract]:
    return [OptionContract(contract_symbol=str(row.get("contractSymbol", "unknown")),
                           strike=float(row.get("strike", 0)), last_price=_number(row.get("lastPrice")),
                           volume=_integer(row.get("volume")), open_interest=_integer(row.get("openInterest")),
                           implied_volatility=_number(row.get("impliedVolatility")))
            for _, row in frame.iterrows()]


def _number(value: Any) -> float | None:
    try:
        result = float(value)
        return None if result != result else result
    except (TypeError, ValueError):
        return None


def _integer(value: Any) -> int | None:
    number = _number(value)
    return int(number) if number is not None else None
