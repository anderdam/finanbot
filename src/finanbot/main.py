"""Entry point for the application.

Initializes a `PostgresUtils` client from settings, ensures the
`finance-tracker` schema exists, and logs available schemas and tables.
"""

import logging
import sys

from app.core.config import get_settings
from app.utils.postgres import PostgresUtils

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> None:
    """Initialize DB client, ensure schema exists, and list schemas/tables.

    Side effects:
    - Uses `get_settings()` to obtain Postgres connection configuration.
    - Creates `PostgresUtils` and exercises its methods:
      - `test_connection()`
      - `create_schema_if_not_exists("finance-tracker")`
      - `list_schemas()`
      - `list_tables("finance-tracker")`
    - Logs results and attempts to gracefully close the DB client if it exposes a `close()` method.
    """
    settings = get_settings()

    db = PostgresUtils(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        schema="finance-tracker",
    )

    try:
        db.test_connection()
        db.create_schema_if_not_exists("finance-tracker")

        schemas = db.list_schemas()
        tables = db.list_tables("finance-tracker")

        logger.info("Available schemas: %s", schemas)
        logger.info("Tables in schema 'finance-tracker': %s", tables)
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


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Application terminated with an error")
        sys.exit(1)
