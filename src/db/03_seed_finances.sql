-- Optional seeds (idempotent where possible). 
-- Run separately after schema is present.

-- Insert a default user (users_id matches schema)
INSERT INTO finances.users (users_id, username, email, display_name)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'localuser',
    'local@example.com',
    'Local User'
)
ON CONFLICT (username) DO NOTHING;

-- Accounts (use accounts_id for PK, user_id as FK referencing users.users_id)
INSERT INTO finances.accounts (
    accounts_id, user_id, acc_name, acc_type, currency, balance
)
VALUES
(
    '10000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'Cash',
    'wallet',
    'BRL',
    500.00
),
(
    '10000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'Checking',
    'bank',
    'BRL',
    1500.00
)
ON CONFLICT (user_id, acc_name) DO NOTHING;

-- Categories
INSERT INTO finances.categories (categories_id, user_id, cat_name, kind, color)
VALUES
(
    '20000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'Groceries',
    'expense',
    '#FF5733'
),
(
    '20000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'Salary',
    'income',
    '#33FF57'
)
ON CONFLICT (user_id, cat_name, kind) DO NOTHING;

-- Sample transactions
INSERT INTO finances.transactions (
    transactions_id,
    user_id,
    account_id,
    category_id,
    occurred_at,
    amount,
    currency,
    tra_type,
    notes
)
VALUES
(
    '30000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    '2025-10-01T12:00:00Z',
    -75.40,
    'BRL',
    'expense',
    'Supermarket'
),
(
    '30000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    '20000000-0000-0000-0000-000000000002',
    '2025-10-05T09:00:00Z',
    2500.00,
    'BRL',
    'income',
    'October salary'
)
ON CONFLICT DO NOTHING;
