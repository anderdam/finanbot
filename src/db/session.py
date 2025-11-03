from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import time
import psycopg2
from psycopg2 import OperationalError

_AsyncSessionLocal = None
_engine = None


def wait_for_postgres(
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    dbname: str | None = None,
    timeout: int = 60,
    interval: float = 1.0,
) -> None:
    host = host or os.environ.get("POSTGRES_HOST", "db")
    port = int(port or os.environ.get("POSTGRES_PORT", 5432))
    user = user or os.environ.get("POSTGRES_USER")
    dbname = dbname or os.environ.get("POSTGRES_DB")
    start = time.time()
    # last_exc: Exception | None = None
    while True:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=os.environ.get("POSTGRES_PASSWORD"),
                dbname=dbname,
                connect_timeout=3,
            )
            conn.close()
            return
        except OperationalError as exc:
            # last_exc = exc
            if time.time() - start > timeout:
                raise RuntimeError(
                    f"Timed out waiting for Postgres at {host}:{port}"
                ) from exc
            time.sleep(interval)


def get_engine():
    global _engine
    if _engine is None:
        from src.core.config import get_settings

        settings = get_settings()
        _engine = create_async_engine(
            settings.async_database_url, future=True, echo=False, pool_pre_ping=True
        )
    return _engine


def get_sessionmaker():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _AsyncSessionLocal


async def get_db():
    SessionLocal = get_sessionmaker()
    async with SessionLocal() as session:
        yield session
