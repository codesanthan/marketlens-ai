# Connectors

All market sources implement `MarketDataConnector` and return typed normalized models containing
connector name (`provider` is retained in the response metadata required by the milestone), source
time, retrieval time, freshness, and warnings. Set `MARKET_DATA_CONNECTOR` to `mock` or `yahoo`.
Yahoo failures are explicit; the application never silently substitutes mock values. See the
[Yahoo connector guide](../packages/connectors/yahoo/README.md).

