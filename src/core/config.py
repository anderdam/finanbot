from functools import lru_cache
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = Field("development")
    log_level: Optional[str] = Field(None)

    postgres_host: str = Field(...)
    postgres_port: int = Field(...)
    postgres_user: str = Field(...)
    postgres_password: str = Field(...)
    postgres_db: str = Field(...)
    db_schema: Optional[str] = Field(None)

    secret_key: str = Field(...)
    jwt_algorithm: str = Field("HS256")
    access_token_expires_minutes: int = Field(60 * 24)

    attachments_dir: Path = Field(Path("/data/attachments"))
    backup_dir: Path = Field(Path("/data/backups"))

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("postgres_port", mode="before")
    def _validate_port(cls, v):
        p = int(v)
        if not (0 < p < 65536):
            raise ValueError("POSTGRES_PORT must be between 1 and 65535")
        return p

    @field_validator("secret_key")
    def _validate_secret_key(cls, v: str):
        if not v or len(v) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters")
        return v

    @field_validator("attachments_dir", "backup_dir", mode="before")
    def _expand_path(cls, v):
        return Path(v).expanduser().resolve()

    @property
    def database_url(self) -> str:
        pw = quote_plus(self.postgres_password)
        return f"postgresql://{self.postgres_user}:{pw}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def async_database_url(self) -> str:
        pw = quote_plus(self.postgres_password)
        return f"postgresql+asyncpg://{self.postgres_user}:{pw}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
