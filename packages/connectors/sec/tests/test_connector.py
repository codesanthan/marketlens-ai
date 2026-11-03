from unittest.mock import AsyncMock

import httpx
import pytest

from packages.connectors.base.symbols import SymbolNotFoundError
from packages.connectors.sec.client import SecClient
from packages.connectors.sec.connector import SecFactsConnector
from packages.connectors.sec.exceptions import SecRateLimitError, SecUnavailableError
from packages.connectors.sec.mapper import map_company_facts


def payload() -> dict[str, object]:
    return {"cik": 320193, "entityName": "APPLE INC", "facts": {"us-gaap": {
        "RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
            {"val": 100, "start": "2024-01-01", "end": "2024-12-31", "filed": "2025-01-31",
             "form": "10-K", "fy": 2024, "fp": "FY", "accn": "0001"},
            {"val": 30, "start": "2025-01-01", "end": "2025-03-31", "filed": "2025-04-30",
             "form": "10-Q", "fy": 2025, "fp": "Q1", "accn": "0002"},
        ]}},
        "Assets": {"units": {"USD": [{"val": 250, "end": "2025-03-31",
            "filed": "2025-04-30", "form": "10-Q", "fy": 2025, "fp": "Q1"}]}},
    }}}


def test_maps_latest_normalized_facts() -> None:
    result = map_company_facts(payload(), "AAPL")
    assert result.entity_name == "APPLE INC"
    assert result.facts[0].metric == "revenue"
    assert result.facts[0].value == 30
    assert result.facts[1].metric == "assets"


def test_newest_tag_wins_when_company_switched_tags() -> None:
    data = {"cik": 1045810, "entityName": "NVIDIA CORP", "facts": {"us-gaap": {
        "RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
            {"val": 26, "start": "2021-02-01", "end": "2022-01-30", "filed": "2022-03-18",
             "form": "10-K", "fy": 2022, "fp": "FY"}]}},
        "Revenues": {"units": {"USD": [
            {"val": 46, "start": "2026-04-27", "end": "2026-07-26", "filed": "2026-08-26",
             "form": "10-Q", "fy": 2027, "fp": "Q2"}]}},
    }}}
    assert map_company_facts(data, "NVDA").facts[0].value == 46


def test_quarter_preferred_over_year_to_date_for_same_end() -> None:
    data = {"cik": 1, "entityName": "X", "facts": {"us-gaap": {"NetIncomeLoss": {"units": {"USD": [
        {"val": 118, "start": "2026-01-26", "end": "2026-07-26", "filed": "2026-08-26",
         "form": "10-Q", "fy": 2027, "fp": "Q2"},
        {"val": 60, "start": "2026-04-27", "end": "2026-07-26", "filed": "2026-08-26",
         "form": "10-Q", "fy": 2027, "fp": "Q2"},
    ]}}}}}
    assert map_company_facts(data, "X").facts[0].value == 60


def test_bank_tags_and_stale_values_are_handled() -> None:
    data = {"cik": 19617, "entityName": "JPMORGAN CHASE & CO", "facts": {"us-gaap": {
        "RevenuesNetOfInterestExpense": {"units": {"USD": [
            {"val": 45, "start": "2026-04-01", "end": "2026-06-30", "filed": "2026-08-01",
             "form": "10-Q", "fy": 2026, "fp": "Q2"}]}},
        "CashAndCashEquivalentsAtCarryingValue": {"units": {"USD": [
            {"val": 26, "end": "2018-12-31", "filed": "2019-02-26", "form": "10-K", "fy": 2018, "fp": "FY"}]}},
    }}}
    facts = map_company_facts(data, "JPM").facts
    assert [(fact.metric, fact.value) for fact in facts] == [("revenue", 45)]


def test_missing_fields_are_skipped() -> None:
    result = map_company_facts({"cik": 1, "facts": {}}, "SPY")
    assert result.facts == [] and result.warnings


@pytest.mark.asyncio
async def test_connector_caches_and_validates() -> None:
    client = AsyncMock()
    client.company_facts.return_value = payload()
    client.ticker_ciks.return_value = {"AAPL": "0000320193", "BRK-B": "0001067983"}
    connector = SecFactsConnector(client)
    await connector.get_company_facts("AAPL")
    await connector.get_company_facts("AAPL")
    client.company_facts.assert_awaited_once_with("0000320193")
    await connector.get_company_facts("brk.b")
    client.company_facts.assert_awaited_with("0001067983")
    client.ticker_ciks.assert_awaited_once()
    with pytest.raises(ValueError):
        await connector.get_company_facts("B@D!")
    with pytest.raises(SymbolNotFoundError):
        await connector.get_company_facts("SPY")


@pytest.mark.asyncio
async def test_health_requires_contact_email() -> None:
    client = AsyncMock()
    client.user_agent = "MarketLens"
    assert not (await SecFactsConnector(client).health()).healthy


@pytest.mark.asyncio
async def test_client_sends_identity_and_parses_json() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["user-agent"] == "MarketLens test@example.com"
        return httpx.Response(200, json={"cik": 320193})
    client = SecClient("MarketLens test@example.com", transport=httpx.MockTransport(handler))
    assert (await client.company_facts("320193"))["cik"] == 320193


@pytest.mark.asyncio
@pytest.mark.parametrize("status,error", [(429, SecRateLimitError), (503, SecUnavailableError)])
async def test_client_maps_sec_errors(status: int, error: type[Exception]) -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(status))
    with pytest.raises(error):
        await SecClient("MarketLens test@example.com", transport=transport).company_facts("320193")


@pytest.mark.asyncio
async def test_client_loads_ticker_map_and_maps_404_to_not_found() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("company_tickers.json"):
            return httpx.Response(200, json={"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
                                             "1": {"cik_str": 1067983, "ticker": "BRK-B", "title": "Berkshire"}})
        return httpx.Response(404)
    client = SecClient("MarketLens test@example.com", transport=httpx.MockTransport(handler))
    assert await client.ticker_ciks() == {"AAPL": "0000320193", "BRK-B": "0001067983"}
    with pytest.raises(SymbolNotFoundError):
        await client.company_facts("884394")
