from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class DatabaseConfig(BaseSettings):
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    db_schema: str | None = Field(None, env="DB_SCHEMA")

    @computed_field
    def database_url(self) -> str:
        pwd = quote_plus(self.postgres_password)
        return f"postgresql://{self.postgres_user}:{pwd}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @computed_field
    def async_database_url(self) -> str:
        pwd = quote_plus(self.postgres_password)
        return f"postgresql+asyncpg://{self.postgres_user}:{pwd}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
