import asyncio
from typing import Any, cast

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from packages.connectors.base.symbols import SymbolNotFoundError

from .exceptions import SecConnectorError, SecRateLimitError, SecUnavailableError


class SecClient:
    base_url = "https://data.sec.gov/api/xbrl/companyfacts"
    tickers_url = "https://www.sec.gov/files/company_tickers.json"

    def __init__(self, user_agent: str, timeout: float = 10, retries: int = 2,
                 transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.user_agent, self.timeout, self.retries = user_agent, timeout, retries
        self.transport = transport

    async def company_facts(self, cik: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self._get_json(f"{self.base_url}/CIK{cik.zfill(10)}.json"))

    async def ticker_ciks(self) -> dict[str, str]:
        """Every SEC-registered operating company's ticker mapped to its 10-digit CIK."""
        rows = await self._get_json(self.tickers_url)
        return {str(row["ticker"]).upper(): str(row["cik_str"]).zfill(10) for row in rows.values()}

    async def _get_json(self, url: str) -> Any:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self.retries + 1), wait=wait_exponential(max=4),
                retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
                reraise=True,
            ):
                with attempt:
                    async with httpx.AsyncClient(timeout=self.timeout,
                                                 transport=self.transport) as client:
                        response = await client.get(url, headers={"User-Agent": self.user_agent,
                                                                  "Accept-Encoding": "gzip, deflate"})
                    if response.status_code == 429:
                        raise SecRateLimitError("SEC fair-access rate limit reached")
                    if response.status_code == 404:
                        raise SymbolNotFoundError("SEC has no company facts for this filer")
                    if response.status_code >= 500:
                        raise SecUnavailableError(f"SEC API unavailable ({response.status_code})")
                    response.raise_for_status()
                    return response.json()
        except (SecConnectorError, SymbolNotFoundError):
            raise
        except (httpx.TimeoutException, asyncio.TimeoutError) as exc:
            raise SecUnavailableError("SEC API request timed out") from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise SecConnectorError(f"SEC API request failed: {type(exc).__name__}") from exc
        raise SecConnectorError("SEC API request failed")
