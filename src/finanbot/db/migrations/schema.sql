-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Helper: set updated_at automatically
CREATE OR REPLACE FUNCTION set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    display_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_users_set_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_timestamp();

-- Accounts (wallet, bank, card)
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name_ TEXT NOT NULL,
    type_ TEXT NOT NULL CHECK (type IN ('wallet', 'bank', 'card')),
    currency CHAR(3) NOT NULL DEFAULT 'BRL' CHECK (currency ~ '^[A-Z]{3}$'),
    balance NUMERIC(18, 2) NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_accounts_set_timestamp
BEFORE UPDATE ON accounts
FOR EACH ROW
EXECUTE FUNCTION set_timestamp();

-- Categories (expense/income)
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name_ TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('expense', 'income')),
    parent_id UUID REFERENCES categories (id) ON DELETE SET NULL,
    color TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    UNIQUE (user_id, name, kind)
);

CREATE TRIGGER trg_categories_set_timestamp
BEFORE UPDATE ON categories
FOR EACH ROW
EXECUTE FUNCTION set_timestamp();

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts (id) ON DELETE RESTRICT,
    category_id UUID REFERENCES categories (id) ON DELETE SET NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    amount NUMERIC(18, 2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'BRL' CHECK (currency ~ '^[A-Z]{3}$'),
    type_ TEXT NOT NULL CHECK (type IN ('expense', 'income', 'transfer')),
    notes TEXT,
    attachment_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_transactions_set_timestamp
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION set_timestamp();

-- Settings
CREATE TABLE IF NOT EXISTS settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    key_ TEXT NOT NULL,
    value_ JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    UNIQUE (user_id, key)
);

CREATE TRIGGER trg_settings_set_timestamp
BEFORE UPDATE ON settings
FOR EACH ROW
EXECUTE FUNCTION set_timestamp();

-- Indexes for queries
CREATE INDEX IF NOT EXISTS idx_transactions_user_occurred
ON transactions (user_id, occurred_at);

CREATE INDEX IF NOT EXISTS idx_transactions_account
ON transactions (account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_category
ON transactions (category_id);
