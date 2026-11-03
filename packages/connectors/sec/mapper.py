from datetime import date, datetime, timezone
from typing import Any

from packages.connectors.base.models import Freshness

from .models import CompanyFacts, FinancialFact

CONCEPTS: dict[str, tuple[str, tuple[str, ...]]] = {
    "revenue": ("Revenue", ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues")),
    "net_income": ("Net income", ("NetIncomeLoss",)),
    "diluted_eps": ("Diluted EPS", ("EarningsPerShareDiluted",)),
    "assets": ("Total assets", ("Assets",)),
    "liabilities": ("Total liabilities", ("Liabilities",)),
    "cash": ("Cash and equivalents", ("CashAndCashEquivalentsAtCarryingValue",)),
}
PREFERRED_UNITS = ("USD", "USD/shares", "shares", "pure")
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A"}


def map_company_facts(payload: dict[str, Any], symbol: str) -> CompanyFacts:
    mapped: list[FinancialFact] = []
    latest_filed: date | None = None
    gaap = payload.get("facts", {}).get("us-gaap", {})
    for metric, (label, aliases) in CONCEPTS.items():
        # Companies switch tags over time (NVIDIA moved from RevenueFromContract... to Revenues), so
        # compare every alias and keep the most recent period rather than the first tag present.
        candidates: list[tuple[str, dict[str, Any]]] = []
        for tag in aliases:
            units = gaap.get(tag, {}).get("units", {})
            unit = next((name for name in PREFERRED_UNITS if name in units), None)
            if unit:
                candidates += [(unit, item) for item in units[unit] if item.get("form") in FORMS]
        if not candidates:
            continue
        # Latest period end; for that end prefer the shortest span (the quarter over year-to-date),
        # then the latest filing (restatements).
        unit, item = max(candidates, key=lambda c: (c[1].get("end", ""), -_span_days(c[1]), c[1].get("filed", "")))
        try:
            fact = FinancialFact(metric=metric, label=label, value=float(item["val"]), unit=unit,
                                 period_start=_optional_date(item.get("start")), period_end=_date(item["end"]),
                                 filed_at=_date(item["filed"]), fiscal_year=item.get("fy"),
                                 fiscal_period=item.get("fp"), form=item["form"],
                                 accession_number=item.get("accn"))
        except (KeyError, TypeError, ValueError):
            continue
        mapped.append(fact)
        latest_filed = max(latest_filed, fact.filed_at) if latest_filed else fact.filed_at
    warnings = [] if mapped else ["No supported SEC financial facts were available"]
    as_of = datetime.combine(latest_filed, datetime.min.time(), timezone.utc) if latest_filed else None
    freshness = Freshness.LIVE_OR_RECENT if latest_filed else Freshness.UNAVAILABLE
    return CompanyFacts(provider="sec_edgar", as_of=as_of, freshness=freshness, warnings=warnings,
                        symbol=symbol, cik=str(payload.get("cik", "")).zfill(10),
                        entity_name=payload.get("entityName"), facts=mapped)


def _date(value: str | None) -> date:
    if not value:
        raise ValueError("Missing SEC fact date")
    return date.fromisoformat(value)


def _span_days(item: dict[str, Any]) -> int:
    try:
        return (date.fromisoformat(item["end"]) - date.fromisoformat(item["start"])).days
    except (KeyError, TypeError, ValueError):
        return 0


def _optional_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None
