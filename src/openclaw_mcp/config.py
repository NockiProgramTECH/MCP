"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings for the MCP server.

    Integration credentials are optional so one unavailable provider cannot stop
    the whole MCP server from starting.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="OPENCLAW_MCP_",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    github_token: SecretStr | None = Field(default=None, validation_alias="GITHUB_TOKEN")
    linkedin_access_token: SecretStr | None = Field(
        default=None, validation_alias="LINKEDIN_ACCESS_TOKEN"
    )
    meta_access_token: SecretStr | None = Field(default=None, validation_alias="META_ACCESS_TOKEN")
    instagram_access_token: SecretStr | None = Field(
        default=None, validation_alias="INSTAGRAM_ACCESS_TOKEN"
    )
    tiktok_access_token: SecretStr | None = Field(default=None, validation_alias="TIKTOK_ACCESS_TOKEN")

    log_level: str = "INFO"
    http_timeout_seconds: float = 15.0
    max_retries: int = 2

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Accept common log-level casing while rejecting unknown values."""
        normalized = value.upper()
        if normalized not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
            raise ValueError("log_level must be a standard logging level")
        return normalized

    @field_validator("http_timeout_seconds")
    @classmethod
    def validate_timeout(cls, value: float) -> float:
        if not 0.1 <= value <= 120:
            raise ValueError("http_timeout_seconds must be between 0.1 and 120 seconds")
        return value

    @field_validator("max_retries")
    @classmethod
    def validate_retries(cls, value: int) -> int:
        if not 0 <= value <= 5:
            raise ValueError("max_retries must be between 0 and 5")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide immutable-by-convention settings object."""
    return Settings()
