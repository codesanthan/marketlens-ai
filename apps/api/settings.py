from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MVP_SYMBOLS = ("SPY", "QQQ", "NVDA", "AAPL", "MSFT", "AMZN", "META", "TSLA")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    market_data_connector: str = "mock"
    allowed_origins: list[str] | str = ["http://localhost:3000"]
    connector_timeout_seconds: float = 10
    connector_retries: int = 2
    connector_cache_ttl_seconds: int = 30
    market_overview_symbols: str = ",".join(MVP_SYMBOLS)
    sec_user_agent: str = "MarketLensAI/0.2 local@example.com"
    sec_cache_ttl_seconds: int = 3600

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        return value.split(",") if isinstance(value, str) and not value.startswith("[") else value

    @field_validator("market_overview_symbols")
    @classmethod
    def validate_overview_symbols(cls, value: str) -> str:
        symbols = tuple(symbol.strip().upper() for symbol in value.split(",") if symbol.strip())
        if not symbols:
            raise ValueError("At least one market overview symbol is required")
        unsupported = set(symbols) - set(MVP_SYMBOLS)
        if unsupported:
            raise ValueError(f"Unsupported market overview symbols: {sorted(unsupported)}")
        return ",".join(dict.fromkeys(symbols))

    @property
    def overview_symbols(self) -> tuple[str, ...]:
        return tuple(self.market_overview_symbols.split(","))


@lru_cache
def get_settings() -> Settings:
    return Settings()
