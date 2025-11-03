#!/usr/bin/env python3
"""
Quick startup job run once when the cron_deactivated_optional container starts.
"""

import logging
import sys
from datetime import datetime

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("cron_deactivated_optional-startup")


def main():
    logger.info(
        "Startup cron_deactivated_optional job ran at %s", datetime.utcnow().isoformat()
    )


if __name__ == "__main__":
    main()
