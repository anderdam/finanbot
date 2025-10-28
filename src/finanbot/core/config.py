from functools import lru_cache
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Environment and logging
    environment: str = Field("development", env="ENVIRONMENT")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # Postgres connection
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    db_schema: str | None = Field(None, env="DB_SCHEMA")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expires_minutes: int = Field(15, env="ACCESS_TOKEN_EXPIRES_MINUTES")

    # Filesystem
    attachments_dir: Path = Field(Path("/data/attachments"), env="ATTACHMENTS_DIR")
    backup_dir: Path = Field(Path("/data/backups"), env="BACKUP_DIR")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("postgres_port")
    def validate_port(cls, v: int) -> int:
        if not (0 < v < 65536):
            raise ValueError("POSTGRES_PORT must be between 1 and 65535")
        return v

    @field_validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters long")
        return v

    @property
    def database_url(self) -> str:
        pwd = quote_plus(self.postgres_password)
        return f"postgresql://{self.postgres_user}:{pwd}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def async_database_url(self) -> str:
        pwd = quote_plus(self.postgres_password)
        return f"postgresql+asyncpg://{self.postgres_user}:{pwd}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def attachments_path(self) -> Path:
        return self.attachments_dir.expanduser().resolve()

    @property
    def backup_path(self) -> Path:
        return self.backup_dir.expanduser().resolve()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
