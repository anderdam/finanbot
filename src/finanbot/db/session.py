from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import sessionmaker

from src.finanbot.core.config import get_settings

engine = create_engine(
    get_settings().database_url, future=True, echo=False, pool_pre_ping=True
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def get_db() -> Generator[SessionType, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
