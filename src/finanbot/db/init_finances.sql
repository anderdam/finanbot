-- Idempotent DB/schema initializer for Postgres docker-entrypoint-initdb.d
-- Place this file under ./db (mapped to /docker-entrypoint-initdb.d).
-- The official Postgres image runs files here only when
--   initializing a fresh data directory.

-- Create role 'anderdam' if missing (run as DB superuser during init)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anderdam') THEN
    CREATE ROLE anderdam WITH LOGIN;
  END IF;
END
$$;

-- Create schema owned by 'anderdam'
CREATE SCHEMA IF NOT EXISTS finances AUTHORIZATION anderdam;

-- Ensure extension is available in this database

-- (requires superuser during init)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Function to update updated_at in finances schema
CREATE OR REPLACE FUNCTION finances.set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Users
CREATE TABLE IF NOT EXISTS finances.users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    display_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
ALTER TABLE finances.users OWNER TO anderdam;

CREATE TRIGGER trg_users_set_timestamp
BEFORE UPDATE ON finances.users
FOR EACH ROW
EXECUTE FUNCTION finances.set_timestamp();

-- Accounts
CREATE TABLE IF NOT EXISTS finances.accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES finances.users (user_id) ON DELETE CASCADE,
    accounts_name TEXT NOT NULL,
    accounts_type TEXT NOT NULL CHECK (type IN ('wallet', 'bank', 'card')),
    currency CHAR(3) NOT NULL DEFAULT 'BRL' CHECK (currency ~ '^[A-Z]{3}$'),
    balance NUMERIC(18, 2) NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
ALTER TABLE finances.accounts OWNER TO anderdam;

CREATE TRIGGER trg_accounts_set_timestamp
BEFORE UPDATE ON finances.accounts
FOR EACH ROW
EXECUTE FUNCTION finances.set_timestamp();

-- Categories
CREATE TABLE IF NOT EXISTS finances.categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES finances.users (user_id) ON DELETE CASCADE,
    category_name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (
        kind IN (
            'expense', 'income', 'transfer', 'savings',
            'housing', 'utilities', 'transportation', 'food',
            'health', 'entertainment', 'personal_care', 'shopping',
            'education', 'donations', 'miscellaneous'
        )
    ),
    parent_id UUID REFERENCES finances.categories (
        category_id
    ) ON DELETE SET NULL,
    color TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    UNIQUE (user_id, name, kind)
);
ALTER TABLE finances.categories OWNER TO anderdam;

CREATE TRIGGER trg_categories_set_timestamp
BEFORE UPDATE ON finances.categories
FOR EACH ROW
EXECUTE FUNCTION finances.set_timestamp();

-- Transactions
CREATE TABLE IF NOT EXISTS finances.transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES finances.users (user_id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES finances.accounts (
        account_id
    ) ON DELETE RESTRICT,
    category_id UUID REFERENCES finances.categories (
        category_id
    ) ON DELETE SET NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    amount NUMERIC(18, 2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'BRL' CHECK (currency ~ '^[A-Z]{3}$'),
    transaction_type TEXT NOT NULL CHECK (
        type IN ('expense', 'income', 'transfer')
    ),
    notes TEXT,
    attachment_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
ALTER TABLE finances.transactions OWNER TO anderdam;

CREATE TRIGGER trg_transactions_set_timestamp
BEFORE UPDATE ON finances.transactions
FOR EACH ROW
EXECUTE FUNCTION finances.set_timestamp();

-- Settings
CREATE TABLE IF NOT EXISTS finances.settings (
    setting_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES finances.users (user_id) ON DELETE CASCADE,
    settings_key TEXT NOT NULL,
    settings_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    UNIQUE (user_id, key)
);
ALTER TABLE finances.settings OWNER TO anderdam;

CREATE TRIGGER trg_settings_set_timestamp
BEFORE UPDATE ON finances.settings
FOR EACH ROW
EXECUTE FUNCTION finances.set_timestamp();

-- Indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_occurred
ON finances.transactions (user_id, occurred_at);

CREATE INDEX IF NOT EXISTS idx_transactions_account
ON finances.transactions (account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_category
ON finances.transactions (category_id);

-- Lock schema to only the anderdam user
REVOKE ALL ON SCHEMA finances FROM public;
GRANT USAGE, CREATE ON SCHEMA finances TO anderdam;

GRANT ALL ON ALL TABLES IN SCHEMA finances TO anderdam;
GRANT ALL ON ALL SEQUENCES IN SCHEMA finances TO anderdam;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA finances TO anderdam;

ALTER DEFAULT PRIVILEGES IN SCHEMA finances GRANT ALL ON TABLES TO anderdam;
ALTER DEFAULT PRIVILEGES IN SCHEMA finances GRANT ALL ON SEQUENCES TO anderdam;
ALTER DEFAULT PRIVILEGES IN SCHEMA finances GRANT ALL ON FUNCTIONS TO anderdam;

ALTER SCHEMA finances OWNER TO anderdam;
