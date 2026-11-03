from unittest.mock import AsyncMock

import httpx
import pytest

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


def test_missing_fields_are_skipped() -> None:
    result = map_company_facts({"cik": 1, "facts": {}}, "SPY")
    assert result.facts == [] and result.warnings


@pytest.mark.asyncio
async def test_connector_caches_and_validates() -> None:
    client = AsyncMock()
    client.company_facts.return_value = payload()
    connector = SecFactsConnector(client)
    await connector.get_company_facts("AAPL")
    await connector.get_company_facts("AAPL")
    client.company_facts.assert_awaited_once()
    with pytest.raises(ValueError):
        await connector.get_company_facts("BAD")


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
