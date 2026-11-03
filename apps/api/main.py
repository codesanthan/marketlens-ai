import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from packages.connectors.base.connector import MarketDataConnector
from packages.connectors.base.models import OptionChain
from packages.connectors.base.symbols import SymbolNotFoundError, normalize_symbol
from packages.connectors.sec import SecFactsConnector
from packages.connectors.sec.exceptions import SecConnectorError
from packages.connectors.yahoo.exceptions import YahooConnectorError

from .dependencies import get_connector, get_sec_connector
from .logging_config import configure_logging
from .settings import get_settings

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()
app = FastAPI(title="MarketLens API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins,
                   allow_credentials=False, allow_methods=["GET"], allow_headers=["*"])


@app.middleware("http")
async def request_context(request: Request, call_next: Any) -> Any:
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))[:128]
    correlation_id = request.headers.get("x-correlation-id", request_id)[:128]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    response.headers["x-correlation-id"] = correlation_id
    logger.info("request_complete", extra={"request_id": request_id, "method": request.method,
                                           "path": request.url.path, "status": response.status_code})
    return response


@app.exception_handler(YahooConnectorError)
async def connector_error(request: Request, exc: YahooConnectorError) -> JSONResponse:
    logger.warning("connector_request_failed", extra={"request_id": request.state.request_id,
                                                       "error_type": type(exc).__name__})
    return JSONResponse(status_code=503, content={"detail": str(exc), "warning": "Live data unavailable",
                                                  "responseTimestamp": _now()})


@app.exception_handler(SymbolNotFoundError)
async def symbol_not_found(request: Request, exc: SymbolNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc), "responseTimestamp": _now()})


@app.exception_handler(SecConnectorError)
async def sec_connector_error(request: Request, exc: SecConnectorError) -> JSONResponse:
    logger.warning("sec_connector_request_failed", extra={"request_id": request.state.request_id,
                                                           "error_type": type(exc).__name__})
    return JSONResponse(status_code=503, content={"detail": str(exc),
                                                  "warning": "SEC facts unavailable",
                                                  "responseTimestamp": _now()})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _symbol(value: str) -> str:
    try:
        return normalize_symbol(value)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


Connector = Annotated[MarketDataConnector, Depends(get_connector)]
SecConnector = Annotated[SecFactsConnector, Depends(get_sec_connector)]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "responseTimestamp": _now()}


@app.get("/ready")
async def ready(connector: Connector) -> dict[str, Any]:
    status = await connector.health()
    if not status.healthy:
        raise HTTPException(503, status.message)
    return {"status": "ready", "connector": status.model_dump(mode="json"), "responseTimestamp": _now()}


@app.get("/api/v1/version")
async def version() -> dict[str, str]:
    return {"version": app.version, "responseTimestamp": _now()}


@app.get("/api/v1/connectors")
async def connectors(connector: Connector, sec: SecConnector) -> dict[str, Any]:
    statuses = await asyncio.gather(connector.health(), sec.health())
    return {"connectors": [status.model_dump(mode="json") for status in statuses],
            "responseTimestamp": _now()}


@app.get("/api/v1/market/overview")
async def overview(connector: Connector) -> dict[str, Any]:
    symbols = settings.overview_symbols
    results = await asyncio.gather(*(connector.get_quote(symbol) for symbol in symbols),
                                   return_exceptions=True)
    quotes, warnings = [], []
    for symbol, result in zip(symbols, results, strict=True):
        if isinstance(result, BaseException):
            warnings.append(f"{symbol}: {type(result).__name__}")
        else:
            quotes.append(result.model_dump(mode="json", by_alias=True))
    return {"quotes": quotes, "warnings": warnings, "responseTimestamp": _now()}


@app.get("/api/v1/tickers/{symbol}")
async def ticker(symbol: str, connector: Connector) -> dict[str, Any]:
    symbol = _symbol(symbol)
    quote, profile = await asyncio.gather(connector.get_quote(symbol), connector.get_company_profile(symbol))
    return {"quote": quote.model_dump(mode="json", by_alias=True),
            "profile": profile.model_dump(mode="json", by_alias=True), "responseTimestamp": _now()}


@app.get("/api/v1/tickers/{symbol}/history")
async def history(symbol: str, connector: Connector,
                  period: Annotated[str, Query(pattern="^(1mo|3mo|6mo|1y)$")] = "1mo") -> dict[str, Any]:
    result = await connector.get_price_history(_symbol(symbol), period)
    return {"history": result.model_dump(mode="json", by_alias=True), "responseTimestamp": _now()}


def _summary(chain: OptionChain) -> dict[str, int]:
    return {"callOpenInterest": sum(item.open_interest or 0 for item in chain.calls),
            "putOpenInterest": sum(item.open_interest or 0 for item in chain.puts),
            "callVolume": sum(item.volume or 0 for item in chain.calls),
            "putVolume": sum(item.volume or 0 for item in chain.puts)}


@app.get("/api/v1/tickers/{symbol}/options")
async def options(symbol: str, connector: Connector, expiration: str | None = None) -> dict[str, Any]:
    symbol = _symbol(symbol)
    expirations = await connector.get_option_expirations(symbol)
    selected = expiration or (expirations.expirations[0] if expirations.expirations else None)
    chain = await connector.get_option_chain(symbol, selected) if selected else None
    return {"expirations": expirations.model_dump(mode="json", by_alias=True),
            "chain": chain.model_dump(mode="json", by_alias=True) if chain else None,
            "summary": _summary(chain) if chain else None, "responseTimestamp": _now()}


@app.get("/api/v1/sec/tickers/{symbol}/facts")
async def sec_facts(symbol: str, sec: SecConnector) -> dict[str, Any]:
    result = await sec.get_company_facts(_symbol(symbol))
    return {"companyFacts": result.model_dump(mode="json", by_alias=True),
            "responseTimestamp": _now()}
