# MarketLens AI — Milestone 1

GCP-native market research foundation with a Next.js dashboard, FastAPI API, replaceable Yahoo
Finance/mock market connectors, and normalized SEC EDGAR Company Facts. Data is for research and
educational use only, not investment advice.

## Start locally

Requires Python 3.12, Node 20, and Docker. Copy `.env.example` to `.env` (never commit it), run
`make install`, then start the two commands printed by `make dev`. Or run `make docker-up` and open
http://localhost:3000; the API is at http://localhost:8000. Stop with `make docker-down`.

Any US-listed stock or ETF works: use the search box in the header or open `/ticker/<SYMBOL>`.
Symbols are 1-5 letters with an optional class suffix (`BRK.B` or `BRK-B`). Malformed symbols and
symbols Yahoo or the SEC does not list return 404. SEC Company Facts come from the SEC's daily
ticker-to-CIK file; ETFs and funds (SPY, QQQ) do not file them. `MARKET_OVERVIEW_SYMBOLS` sets
the dashboard list (up to 20).

Select `MARKET_DATA_CONNECTOR=mock` for deterministic data or `yahoo` for live/latest Yahoo data.
Use `MARKET_OVERVIEW_SYMBOLS=SPY` to limit dashboard quote requests while retaining all ticker routes.
Set `SEC_USER_AGENT` to an application name and monitored contact email before using SEC data.
Configure `ALLOWED_ORIGINS`, connector timeout/retries/cache TTL, `API_BASE_URL` (server-side web
container), and `NEXT_PUBLIC_API_BASE_URL` only if browser-visible API access is later required.

Run `make test`, `make lint`, and `make build`. See [GCP deployment](docs/gcp-deployment.md),
[architecture](docs/architecture.md), and [connectors](docs/connectors.md).

```text
apps/web                  Next.js application
apps/api                  FastAPI application
packages/connectors/base  connector contract and normalized models
packages/connectors/yahoo Yahoo Finance adapter
packages/connectors/mock  deterministic development adapter
packages/connectors/sec   official SEC Company Facts adapter
docs                      operations and design documentation
infra/gcp                 GCP bootstrap
tests                     API and connector tests
```
