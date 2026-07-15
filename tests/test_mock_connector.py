import pytest

from packages.connectors.mock import MockMarketDataConnector


@pytest.mark.asyncio
async def test_mock_supports_operations() -> None:
    connector = MockMarketDataConnector()
    assert (await connector.get_quote("SPY")).price is not None
    assert (await connector.get_company_profile("SPY")).company_name
    assert (await connector.get_price_history("SPY", "1mo")).bars
    assert (await connector.get_option_expirations("SPY")).expirations
    assert (await connector.health()).healthy

