from functools import lru_cache
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from pydantic import ConfigDict, Field, computed_field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Postgres connection settings
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., env="POSTGRES_DB")

    # Application secrets / behavior
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expires_minutes: int = Field(15, env="ACCESS_TOKEN_EXPIRES_MINUTES")

    # Filesystem locations (use Path for convenience)
    attachments_dir: Path = Field(Path("/data/attachments"), env="ATTACHMENTS_DIR")
    backup_dir: Path = Field(Path("/data/backups"), env="BACKUP_DIR")

    # Optional DB schema name
    schema: Optional[str] = Field(None, env="DB_SCHEMA")

    # read .env and ignore unknown keys
    model_config = ConfigDict(env_file=".env", extra="ignore")

    @field_validator("postgres_port")
    def _validate_port(cls, v: int) -> int:
        if not (0 < v < 65536):
            raise ValueError("POSTGRES_PORT must be an integer between 1 and 65535")
        return v

    @field_validator("secret_key")
    def _validate_secret_key(cls, v: str) -> str:
        if not v:
            raise ValueError("SECRET_KEY must be set")
        if len(v) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters long")
        return v

    @computed_field
    def database_url(self) -> str:
        """Synchronous SQLAlchemy / psycopg2 URL (escaped password)."""
        pwd = quote_plus(self.postgres_password)
        return f"postgresql://{self.postgres_user}:{pwd}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @computed_field
    def async_database_url(self) -> str:
        """Async DB driver URL (asyncpg / SQLAlchemy async)."""
        pwd = quote_plus(self.postgres_password)
        return f"postgresql+asyncpg://{self.postgres_user}:{pwd}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @computed_field
    def attachments_path(self) -> Path:
        """Resolved Path for attachments_dir (expanduser + resolve)."""
        return self.attachments_dir.expanduser().resolve()

    class Config:  # type: ignore
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    # For quick testing

    settings = Settings()
    print("Database URL:", settings.database_url)
    print("Async Database URL:", settings.async_database_url)
    print("Attachments Path:", settings.attachments_path)
