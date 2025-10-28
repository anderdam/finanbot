"""Entry point for the FinanBot application.

Initializes the FastAPI app, sets up CORS, and ensures the Postgres schema exists.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.finanbot.core.config import get_settings
from src.finanbot.utils.postgres import PostgresUtils
from src.finanbot.api.v1 import transactions, attachments
from src.finanbot.core.logging import setup_logging, get_logger

setup_logging()

logger = get_logger(__name__)


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic for FastAPI."""
    db = PostgresUtils(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        # schema="finances",
    )

    database_name = settings.postgres_db

    try:
        db.test_connection()
        # db.create_schema_if_not_exists(database_name)

        schemas = db.list_schemas()
        tables = db.list_tables(database_name)

        logger.info("Available schemas: %s", schemas)
        logger.info(f"Tables in schema {database_name}: %s", tables)
    except Exception:
        logger.exception("An error occurred while interacting with the database")
        raise
    finally:
        close_fn = getattr(db, "close", None)
        if callable(close_fn):
            try:
                close_fn()
            except Exception:
                logger.exception("Failed to close the database client")

    yield  # Continue serving FastAPI
    # No shutdown logic needed here


app = FastAPI(title="FinanBot API", lifespan=lifespan)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(transactions.router)
app.include_router(attachments.router)
