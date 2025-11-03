"""Entry point for the FinanBot application.

Initializes the FastAPI app, sets up CORS, and ensures the Postgres schema exists.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import get_settings
from src.db.session import wait_for_postgres
from src.utils.postgres import PostgresUtils
from src.api.v1 import router
from src.core.logger import setup_logging, get_logger

from fastapi import status
from fastapi.responses import JSONResponse
import anyio

setup_logging()

logger = get_logger(__name__)


settings = get_settings()
wait_for_postgres(
    host=settings.postgres_host,
    port=settings.postgres_port,
    user=settings.postgres_user,
    dbname=settings.postgres_db,
    timeout=60,
)


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
app.include_router(router.router, prefix="/v1")
# app.include_router(attachments.router)


@app.get("/health")
async def health():
    """
    Liveness probe used by Docker and orchestrators.
    Returns HTTP 200 when the app is up and serving requests.
    """
    return {"status": "ok"}


@app.get("/ready")
async def readiness():
    """
    Readiness probe: quick check of DB connectivity.
    Calls the existing PostgresUtils.test_connection() in a thread to avoid blocking.
    Returns 200 when DB is reachable, 503 otherwise.
    """
    try:

        def check_db():
            db = PostgresUtils(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
            )
            try:
                db.test_connection()
            finally:
                close_fn = getattr(db, "close", None)
                if callable(close_fn):
                    try:
                        close_fn()
                    except Exception:
                        logger.exception("Failed to close DB client in readiness check")

        await anyio.to_thread.run_sync(check_db)
    except Exception:
        logger.exception("Readiness check failed: DB unreachable")
        return JSONResponse(
            {"status": "db-unavailable"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return {"status": "ok"}
