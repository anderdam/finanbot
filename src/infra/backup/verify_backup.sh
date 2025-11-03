#!/bin/bash

# To use:
# cd backup_ssd
# sha256sum db_*.sql.gz attachments_*.tar.gz > checksums.txt
# Then run this script to verify
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
CHECKSUM_FILE="$BACKUP_DIR/checksums.txt"

# Generate fresh checksums
echo "Verifying backup integrity..."
cd "$BACKUP_DIR"
sha256sum -c "$CHECKSUM_FILE"
