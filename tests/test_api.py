from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from apps.api.dependencies import get_connector, get_sec_connector
from apps.api.main import app
from apps.api.settings import get_settings
from packages.connectors.mock import MockMarketDataConnector
from packages.connectors.sec.connector import SecFactsConnector
from packages.connectors.sec.tests.test_connector import payload

app.dependency_overrides[get_connector] = MockMarketDataConnector
sec_client = AsyncMock()
sec_client.user_agent = "MarketLens tests@example.com"
sec_client.company_facts.return_value = payload()
sec_client.ticker_ciks.return_value = {"AAPL": "0000320193"}
app.dependency_overrides[get_sec_connector] = lambda: SecFactsConnector(sec_client)
client = TestClient(app)


def test_health_and_ready() -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/ready").json()["status"] == "ready"


def test_overview() -> None:
    response = client.get("/api/v1/market/overview")
    assert response.status_code == 200
    assert len(response.json()["quotes"]) == len(get_settings().overview_symbols)


def test_ticker_and_invalid_symbol() -> None:
    assert client.get("/api/v1/tickers/SPY").json()["quote"]["symbol"] == "SPY"
    assert client.get("/api/v1/tickers/NOPE").status_code == 404
    assert client.get("/api/v1/tickers/B@D!").status_code == 404


def test_history_and_options_summary() -> None:
    assert len(client.get("/api/v1/tickers/SPY/history").json()["history"]["bars"]) == 30
    summary = client.get("/api/v1/tickers/SPY/options").json()["summary"]
    assert summary == {"callOpenInterest": 500, "putOpenInterest": 500,
                       "callVolume": 200, "putVolume": 200}


def test_version_and_connectors() -> None:
    assert client.get("/api/v1/version").json()["version"] == "0.1.0"
    assert client.get("/api/v1/connectors").json()["connectors"][0]["healthy"] is True


def test_sec_company_facts() -> None:
    response = client.get("/api/v1/sec/tickers/AAPL/facts")
    assert response.status_code == 200
    facts = response.json()["companyFacts"]
    assert facts["provider"] == "sec_edgar"
    assert facts["facts"][0]["metric"] == "revenue"
    assert client.get("/api/v1/sec/tickers/QQQ/facts").status_code == 404
