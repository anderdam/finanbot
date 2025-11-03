#!/usr/bin/env python3
"""
Example hourly job. Triggers a backend endpoint or run local module code.
Adjust FINANBOT_BACKEND_URL or replace HTTP call with direct imports.
"""

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("cron_deactivated_optional-hourly")


def main():
    logger.info("Starting hourly job")
    backend_url = os.getenv("FINANBOT_BACKEND_URL", "http://finanbot:8000")
    try:
        import urllib.request

        with urllib.request.urlopen(f"{backend_url}/tasks/run-hourly") as r:
            logger.info("Triggered backend task, status=%s", r.status)
    except Exception as exc:
        logger.exception("Failed to trigger backend: %s", exc)

    logger.info("Hourly job finished at %s", datetime.utcnow().isoformat())


if __name__ == "__main__":
    main()
