from fastapi.testclient import TestClient

from apps.api.dependencies import get_connector
from apps.api.main import app
from packages.connectors.mock import MockMarketDataConnector

app.dependency_overrides[get_connector] = MockMarketDataConnector
client = TestClient(app)


def test_health_and_ready() -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/ready").json()["status"] == "ready"


def test_overview() -> None:
    response = client.get("/api/v1/market/overview")
    assert response.status_code == 200
    assert len(response.json()["quotes"]) == 8


def test_ticker_and_invalid_symbol() -> None:
    assert client.get("/api/v1/tickers/SPY").json()["quote"]["symbol"] == "SPY"
    assert client.get("/api/v1/tickers/NOPE").status_code == 404


def test_history_and_options_summary() -> None:
    assert len(client.get("/api/v1/tickers/SPY/history").json()["history"]["bars"]) == 30
    summary = client.get("/api/v1/tickers/SPY/options").json()["summary"]
    assert summary == {"callOpenInterest": 500, "putOpenInterest": 500,
                       "callVolume": 200, "putVolume": 200}


def test_version_and_connectors() -> None:
    assert client.get("/api/v1/version").json()["version"] == "0.1.0"
    assert client.get("/api/v1/connectors").json()["connectors"][0]["healthy"] is True

