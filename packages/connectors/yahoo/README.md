# Yahoo Finance connector

This connector adapts `yfinance` data into MarketLens' typed, connector-neutral models. It supports
quotes, company profiles, price history, option expirations, option chains, calls, puts, volume,
open interest, and implied volatility.

`YahooClient` owns blocking I/O, timeouts, and exponential retries. `YahooMarketDataConnector`
validates the MVP allowlist and maintains a process-local TTL cache (30 seconds by default).
`mapper.py` converts Yahoo/pandas values without inventing missing data and classifies freshness.

Yahoo Finance is an unofficial, best-effort data source. Fields may be missing, delayed, changed,
rate-limited, or temporarily unavailable; it is unsuitable for execution or trading decisions.
Failures remain visible and mock data is used only when explicitly configured.

To replace it, implement `MarketDataConnector`, return the normalized base models, and select the
new connector in the API factory. Routes and UI require no provider-specific changes.

Example: `await connector.get_quote("SPY")`. Run tests with `pytest packages/connectors/yahoo/tests`.

