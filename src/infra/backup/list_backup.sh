#!/bin/bash
set -e

# Load environment
ENV_FILE="$(dirname "$0")/.env"
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' "$ENV_FILE" | xargs)
else
  echo "Missing .env file at $ENV_FILE"
  exit 1
fi

BACKUP_DIR="${BACKUP_DIR:-/mnt/backup_ssd}"

echo "Available backups:"
# shellcheck disable=SC2010
ls "$BACKUP_DIR" | grep -E '^db_.*\.sql\.gz$' | sed 's/^db_//;s/\.sql\.gz$//' | sort
