#!/usr/bin/env bash
set -euo pipefail

: "${POSTGRES_USER:?}"
: "${POSTGRES_DB:?}"

# run only if schema 'finances' does not exist
if psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -tAc "SELECT 1 FROM information_schema.schemata WHERE schema_name='finances'" | grep -q 1; then
  echo "Schema 'finances' already exists; skipping init SQL."
  exit 0
fi

echo "Applying init SQL..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init_finances.sql
echo "Init applied."