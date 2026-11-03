from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pandas as pd
import pytest

from packages.connectors.base.models import Freshness
from packages.connectors.base.symbols import SymbolNotFoundError
from packages.connectors.yahoo.client import YahooClient
from packages.connectors.yahoo.connector import YahooMarketDataConnector
from packages.connectors.yahoo.exceptions import YahooTimeoutError
from packages.connectors.yahoo.mapper import freshness


def info(**extra: object) -> dict[str, object]:
    return {"regularMarketTime": datetime.now(timezone.utc).timestamp(), "currentPrice": 100,
            "regularMarketChange": 2, "regularMarketChangePercent": 2.04,
            "regularMarketVolume": 10, "marketCap": 1000, **extra}


@pytest.mark.asyncio
async def test_normalizes_and_caches_quote() -> None:
    client = AsyncMock()
    client.info.return_value = info()
    connector = YahooMarketDataConnector(client, 30)
    assert (await connector.get_quote("SPY")).price == 100
    await connector.get_quote("SPY")
    client.info.assert_awaited_once()


@pytest.mark.asyncio
async def test_missing_fields_are_not_invented() -> None:
    client = AsyncMock()
    client.info.return_value = {}
    quote = await YahooMarketDataConnector(client).get_quote("SPY")
    assert quote.price is None and quote.freshness == Freshness.UNAVAILABLE and quote.warnings


@pytest.mark.asyncio
async def test_invalid_symbol() -> None:
    with pytest.raises(ValueError):
        await YahooMarketDataConnector(AsyncMock()).get_quote("B@D!")


@pytest.mark.asyncio
async def test_any_listed_symbol_is_accepted_and_unknown_is_not_found() -> None:
    client = AsyncMock()
    client.info.side_effect = lambda symbol: (
        {"quoteType": "EQUITY", "regularMarketPrice": 556.11} if symbol == "BRK-B" else {"trailingPegRatio": None})
    connector = YahooMarketDataConnector(client)
    assert (await connector.get_quote("brk.b")).price == 556.11
    with pytest.raises(SymbolNotFoundError):
        await connector.get_quote("ZZZQX")


@pytest.mark.asyncio
async def test_history_and_options_mapping() -> None:
    client = AsyncMock()
    client.info.return_value = {"quoteType": "ETF"}
    index = pd.DatetimeIndex([datetime.now(timezone.utc)])
    client.history.return_value = pd.DataFrame([{"Open":1,"High":2,"Low":.5,"Close":1.5,"Volume":20}], index=index)
    frame = pd.DataFrame([{"contractSymbol":"SPY1","strike":100,"volume":2,"openInterest":3,"impliedVolatility":.2}])
    client.option_chain.return_value = SimpleNamespace(calls=frame, puts=frame)
    connector = YahooMarketDataConnector(client)
    assert (await connector.get_price_history("SPY", "1mo")).bars[0].close == 1.5
    assert (await connector.get_option_chain("SPY", "2030-01-01")).calls[0].open_interest == 3


def test_stale_classification() -> None:
    now = datetime.now(timezone.utc)
    assert freshness(now - timedelta(days=2), now) == Freshness.STALE
    assert freshness(now - timedelta(hours=2), now) == Freshness.DELAYED


@pytest.mark.asyncio
async def test_timeout_mapping_and_retry() -> None:
    calls = 0
    def slow() -> None:
        nonlocal calls
        calls += 1
        raise TimeoutError
    client = YahooClient(timeout=.01, retries=1)
    with pytest.raises(YahooTimeoutError):
        await client._call(slow)
    assert calls == 2
