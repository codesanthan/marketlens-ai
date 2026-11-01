from functools import lru_cache

from packages.connectors.base.connector import MarketDataConnector
from packages.connectors.mock import MockMarketDataConnector
from packages.connectors.sec import SecFactsConnector
from packages.connectors.sec.client import SecClient
from packages.connectors.yahoo import YahooMarketDataConnector
from packages.connectors.yahoo.client import YahooClient

from .settings import MVP_SYMBOLS, get_settings


@lru_cache
def get_connector() -> MarketDataConnector:
    settings = get_settings()
    if settings.market_data_connector == "mock":
        return MockMarketDataConnector()
    if settings.market_data_connector == "yahoo":
        return YahooMarketDataConnector(
            YahooClient(settings.connector_timeout_seconds, settings.connector_retries),
            set(MVP_SYMBOLS), settings.connector_cache_ttl_seconds,
        )
    raise RuntimeError(f"Unknown connector: {settings.market_data_connector}")


@lru_cache
def get_sec_connector() -> SecFactsConnector:
    settings = get_settings()
    return SecFactsConnector(
        SecClient(settings.sec_user_agent, settings.connector_timeout_seconds,
                  settings.connector_retries), settings.sec_cache_ttl_seconds,
    )
