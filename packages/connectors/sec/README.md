# SEC EDGAR Company Facts connector

This connector uses the official, unauthenticated SEC Company Facts API to normalize a focused set
of US-GAAP facts: revenue, net income, diluted EPS, assets, liabilities, and cash. It performs one
request per company, caches results in process for one hour by default, and sends the configured
`SEC_USER_AGENT`. Set that value to an application name plus a monitored contact email.

Facts are selected from 10-K/10-Q (and supported foreign issuer equivalents) by latest filing date.
Missing concepts remain absent; the connector does not infer values. Issuer-specific XBRL tags,
amendments, fiscal calendars, and units can reduce comparability. ETF symbols may have no supported
US-GAAP facts. Run tests with `pytest packages/connectors/sec/tests`.
