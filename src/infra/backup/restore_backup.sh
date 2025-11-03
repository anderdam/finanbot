#!/bin/bash
set -e

if [ "$1" == "list" ]; then
  echo "Available backups:"
  ls "$BACKUP_DIR" | grep -E 'db_.*\.sql\.gz' | sed 's/db_//;s/\.sql\.gz//'
  exit 0
fi


# Load environment variables
ENV_FILE="$(dirname "$0")/.env"
if [ -f "$ENV_FILE" ]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
else
  echo "Missing .env file at $ENV_FILE"
  exit 1
fi

# Input: timestamp or filename prefix
if [ -z "$1" ]; then
  echo "Usage: $0 <timestamp>"
  echo "Example: $0 2025-10-28_14-00"
  exit 1
fi

TIMESTAMP="$1"
BACKUP_DIR="${BACKUP_DIR:-/data/backups}"
ATTACHMENTS_DIR="${ATTACHMENTS_DIR:-/data/attachments}"

DB_FILE="$BACKUP_DIR/db_${TIMESTAMP}.sql.gz"
ATTACHMENTS_FILE="$BACKUP_DIR/attachments_${TIMESTAMP}.tar.gz"

echo "You are about to restore backup from: $TIMESTAMP"
read -p "Are you sure? (y/N): " confirm
if [[ "$confirm" != "y" ]]; then
  echo "Restore cancelled."
  exit 0
fi


# Restore database
if [ -f "$DB_FILE" ]; then
  echo "Restoring database from $DB_FILE..."
  gunzip -c "$DB_FILE" | psql -U "$POSTGRES_USER" -h "$POSTGRES_HOST" "$POSTGRES_DB"
else
  echo "Database backup not found: $DB_FILE"
fi

# Restore attachments
if [ -f "$ATTACHMENTS_FILE" ]; then
  echo "Restoring attachments from $ATTACHMENTS_FILE..."
  tar -xzf "$ATTACHMENTS_FILE" -C "$ATTACHMENTS_DIR"

  python3 "$(dirname "$0")\send_email.py" \
  "Finanbot Restore Completed" \
  "✅ Restore completed for backup: $TIMESTAMP"
else
	python3 "$(dirname "$0")\send_email.py" \
	"Finanbot Restore Failed" \
  "❌ Restore failed for backup: $TIMESTAMP"

  echo "Attachments archive not found: $ATTACHMENTS_FILE"
fi

LOG_FILE="$BACKUP_DIR/restore.log"
echo "$(date) - Restored backup: $TIMESTAMP" >> "$LOG_FILE"

echo "Restore complete."
