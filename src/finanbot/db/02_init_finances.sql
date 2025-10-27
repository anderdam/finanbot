-- Idempotent schema + canonical tables for 'finances' schema
-- Designed to be executed as the application DB user
--(wrapper runs it as $POSTGRES_USER)

CREATE SCHEMA IF NOT EXISTS finances AUTHORIZATION current_user;

CREATE OR REPLACE FUNCTION finances.set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- users (primary key column follows pattern: users_id)
CREATE TABLE IF NOT EXISTS finances.users (
    users_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    display_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_users_set_timestamp'
        AND tgrelid = 'finances.users'::regclass
  ) THEN
    CREATE TRIGGER trg_users_set_timestamp
    BEFORE UPDATE ON finances.users
    FOR EACH ROW EXECUTE FUNCTION finances.set_timestamp();
  END IF;
END;
$$;

-- accounts (accounts_id and acc_name/acc_type)
CREATE TABLE IF NOT EXISTS finances.accounts (
    accounts_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES finances.users (
        users_id
    ) ON DELETE CASCADE,
    acc_name TEXT NOT NULL,
    acc_type TEXT NOT NULL CHECK (acc_type IN ('wallet', 'bank', 'card')),
    currency CHAR(3) NOT NULL DEFAULT 'BRL' CHECK (currency ~ '^[A-Z]{3}$'),
    balance NUMERIC(18, 2) NOT NULL DEFAULT 0,
    details JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

ALTER TABLE finances.accounts
ADD CONSTRAINT uq_finances_accounts_user_acc_name UNIQUE (user_id, acc_name);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_accounts_set_timestamp' AND tgrelid = 'finances.accounts'::regclass
  ) THEN
    CREATE TRIGGER trg_accounts_set_timestamp
    BEFORE UPDATE ON finances.accounts
    FOR EACH ROW EXECUTE FUNCTION finances.set_timestamp();
  END IF;
END;
$$;

-- categories (categories_id and cat_name)
CREATE TABLE IF NOT EXISTS finances.categories (
    categories_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES finances.users (
        users_id
    ) ON DELETE CASCADE,
    cat_name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (
        kind IN (
            'expense', 'income', 'transfer', 'savings', 'housing', 'utilities',
            'transportation',
            'food',
            'health',
            'entertainment',
            'personal_care',
            'shopping', 'education', 'donations', 'miscellaneous'
        )
    ),
    parent_id UUID REFERENCES finances.categories (
        categories_id
    ) ON DELETE SET NULL,
    color TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    UNIQUE (user_id, cat_name, kind)
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_categories_set_timestamp' AND tgrelid = 'finances.categories'::regclass
  ) THEN
    CREATE TRIGGER trg_categories_set_timestamp
    BEFORE UPDATE ON finances.categories
    FOR EACH ROW EXECUTE FUNCTION finances.set_timestamp();
  END IF;
END;
$$;

-- transactions (transactions_id and tra_type)
CREATE TABLE IF NOT EXISTS finances.transactions (
    transactions_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES finances.users (
        users_id
    ) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES finances.accounts (
        accounts_id
    ) ON DELETE RESTRICT,
    category_id UUID REFERENCES finances.categories (
        categories_id
    ) ON DELETE SET NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    amount NUMERIC(18, 2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'BRL' CHECK (currency ~ '^[A-Z]{3}$'),
    tra_type TEXT NOT NULL CHECK (
        tra_type IN ('expense', 'income', 'transfer')
    ),
    notes TEXT,
    attachment_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_transactions_set_timestamp' AND tgrelid = 'finances.transactions'::regclass
  ) THEN
    CREATE TRIGGER trg_transactions_set_timestamp
    BEFORE UPDATE ON finances.transactions
    FOR EACH ROW EXECUTE FUNCTION finances.set_timestamp();
  END IF;
END;
$$;

-- settings (settings_id, set_key/set_value)
CREATE TABLE IF NOT EXISTS finances.settings (
    settings_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES finances.users (
        users_id
    ) ON DELETE CASCADE,
    set_key TEXT NOT NULL,
    set_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    UNIQUE (user_id, set_key)
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'trg_settings_set_timestamp' AND tgrelid = 'finances.settings'::regclass
  ) THEN
    CREATE TRIGGER trg_settings_set_timestamp
    BEFORE UPDATE ON finances.settings
    FOR EACH ROW EXECUTE FUNCTION finances.set_timestamp();
  END IF;
END;
$$;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_occurred
ON finances.transactions (
    user_id, occurred_at
);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON finances.transactions (
    account_id
);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON finances.transactions (
    category_id
);

-- Grants for the current DB user (the wrapper runs as $POSTGRES_USER)
REVOKE ALL ON SCHEMA finances FROM public;
GRANT USAGE, CREATE ON SCHEMA finances TO current_user;

GRANT ALL ON ALL TABLES IN SCHEMA finances TO current_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA finances TO current_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA finances TO current_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA finances
GRANT ALL ON TABLES TO current_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA finances
GRANT ALL ON SEQUENCES TO current_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA finances
GRANT ALL ON FUNCTIONS TO current_user;

ALTER SCHEMA finances OWNER TO current_user;
