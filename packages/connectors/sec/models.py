from datetime import date

from pydantic import BaseModel

from packages.connectors.base.models import ConnectorMetadata


class FinancialFact(BaseModel):
    metric: str
    label: str
    value: float
    unit: str
    period_start: date | None = None
    period_end: date
    filed_at: date
    fiscal_year: int | None = None
    fiscal_period: str | None = None
    form: str
    accession_number: str | None = None


class CompanyFacts(ConnectorMetadata):
    symbol: str
    cik: str
    entity_name: str | None = None
    facts: list[FinancialFact]
