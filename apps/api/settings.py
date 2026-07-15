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

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        return value.split(",") if isinstance(value, str) and not value.startswith("[") else value


@lru_cache
def get_settings() -> Settings:
    return Settings()

