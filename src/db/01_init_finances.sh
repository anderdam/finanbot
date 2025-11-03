#!/usr/bin/env bash
set -euo pipefail

: "${POSTGRES_USER:?POSTGRES_USER required}"
: "${POSTGRES_DB:?POSTGRES_DB required}"

# Create uuid-ossp extension as the postgres superuser (safe if it already exists)
psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "$POSTGRES_DB" -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";' || true

# Sentinel: check for the canonical users table/column in the finances schema
if psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -tAc \
    "SELECT 1 FROM information_schema.tables WHERE table_schema='finances' AND table_name='users';" | grep -q 1; then
  echo "Schema 'finances' already initialized; skipping schema SQL."
  exit 0
fi

echo "Applying schema SQL as user '$POSTGRES_USER' to database '$POSTGRES_DB'..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/02_init_finances.sql
echo "Schema applied."

# Optionally run seeds if present and desired (uncomment to run automatically)
# echo "Applying seeds..."
# psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/03_seed_finances.sql
# echo "Seeds applied."


