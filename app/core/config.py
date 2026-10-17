from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database connection URL (e.g. postgresql://user:password@localhost:5432/dbname)
    DATABASE_URL: str

    # Security & Admin auth
    ADMIN_API_KEY: str = "dev-secret-key"

    # Crawler Politeness & Limits
    USER_AGENT: str = "JobDiscoveryBot/1.0 (+https://example.com/bot;"
    DEFAULT_CRAWL_INTERVAL_HOURS: int = 6
    RATE_LIMIT_PER_DOMAIN_RPS: float = 1.0
    MAX_PAYLOAD_BYTES: int = 5 * 1024 * 1024  # 5 MB safety cap

    # Server Settings
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # Validator: ensures DEBUG values like "True", "1", "true" are parsed cleanly
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "t", "yes", "debug")
        return False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global singleton instance to import across the app
settings = Settings()