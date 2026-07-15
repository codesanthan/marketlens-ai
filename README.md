# MarketLens AI — Milestone 1

GCP-native market research foundation with a Next.js dashboard, FastAPI API, and replaceable Yahoo
Finance/mock connectors. Data is for research and educational use only, not investment advice.

## Start locally

Requires Python 3.12, Node 20, and Docker. Copy `.env.example` to `.env` (never commit it), run
`make install`, then start the two commands printed by `make dev`. Or run `make docker-up` and open
http://localhost:3000; the API is at http://localhost:8000. Stop with `make docker-down`.

Select `MARKET_DATA_CONNECTOR=mock` for deterministic data or `yahoo` for live/latest Yahoo data.
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
docs                      operations and design documentation
infra/gcp                 GCP bootstrap
tests                     API and connector tests
```

