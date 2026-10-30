"""Application settings read from environment variables (docs/app-spec.md, section 7)."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    # No default on purpose: the secret must come from the environment (GT-02).
    jwt_secret: str
    jwt_expire_minutes: int = 30

    cors_origins: Annotated[list[str], NoDecode] = []

    s3_bucket: str
    # Empty in AWS (real S3 through the IAM role); moto locally and in CI (ADR-0009).
    s3_endpoint_url: str | None = None
    attachment_cache_dir: Path = Path("/tmp/ticketing-attachments")
    max_upload_bytes: int = 5 * 1024 * 1024
    allowed_content_types: Annotated[list[str], NoDecode] = [
        "text/plain",
        "application/pdf",
        "image/png",
        "image/jpeg",
    ]

    log_level: str = "INFO"

    @field_validator("s3_endpoint_url", mode="before")
    @classmethod
    def empty_as_none(cls, value: object) -> object:
        # S3_ENDPOINT_URL= (set but empty) means real S3, same as not set.
        return value or None

    @field_validator("cors_origins", "allowed_content_types", mode="before")
    @classmethod
    def split_comma_separated(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
