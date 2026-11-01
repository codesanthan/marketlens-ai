# Connectors

All market sources implement `MarketDataConnector` and return typed normalized models containing
connector name (`provider` is retained in the response metadata required by the milestone), source
time, retrieval time, freshness, and warnings. Set `MARKET_DATA_CONNECTOR` to `mock` or `yahoo`.
Yahoo failures are explicit; the application never silently substitutes mock values. See the
[Yahoo connector guide](../packages/connectors/yahoo/README.md).

The SEC EDGAR connector uses the official Company Facts API and exposes revenue, net income, diluted
EPS, assets, liabilities, and cash through `/api/v1/sec/tickers/{symbol}/facts`. It requires a
declared `SEC_USER_AGENT`, caches each company for one hour, and omits unavailable concepts instead
of deriving values. See the [SEC connector guide](../packages/connectors/sec/README.md).
