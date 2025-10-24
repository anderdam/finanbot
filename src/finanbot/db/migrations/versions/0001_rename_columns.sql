-- Idempotent column-rename migration.
-- Run this against the target DB (schema = finances).
-- It will rename legacy columns if present.
DO $$
BEGIN
  -- users.id -> users_id
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'users' AND column_name = 'id'
  ) THEN
    EXECUTE 'ALTER TABLE finances.users RENAME COLUMN id TO users_id';
  END IF;

  -- accounts.id -> accounts_id ; accounts.name -> acc_name ; accounts.type -> acc_type
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'accounts' AND column_name = 'id'
  ) THEN
    EXECUTE 'ALTER TABLE finances.accounts RENAME COLUMN id TO accounts_id';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'accounts' AND column_name = 'name'
  ) THEN
    EXECUTE 'ALTER TABLE finances.accounts RENAME COLUMN name TO acc_name';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'accounts' AND column_name = 'type'
  ) THEN
    EXECUTE 'ALTER TABLE finances.accounts RENAME COLUMN type TO acc_type';
  END IF;

  -- categories.id -> categories_id ; categories.name -> cat_name
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'categories' AND column_name = 'id'
  ) THEN
    EXECUTE 'ALTER TABLE finances.categories RENAME COLUMN id TO categories_id';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'categories' AND column_name = 'name'
  ) THEN
    EXECUTE 'ALTER TABLE finances.categories RENAME COLUMN name TO cat_name';
  END IF;

  -- transactions.id -> transactions_id ; transactions.type -> tra_type
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'transactions' AND column_name = 'id'
  ) THEN
    EXECUTE 'ALTER TABLE finances.transactions RENAME COLUMN id TO transactions_id';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'transactions' AND column_name = 'type'
  ) THEN
    EXECUTE 'ALTER TABLE finances.transactions RENAME COLUMN type TO tra_type';
  END IF;

  -- settings.id -> settings_id ; settings.key -> set_key ; settings.value -> set_value
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'settings' AND column_name = 'id'
  ) THEN
    EXECUTE 'ALTER TABLE finances.settings RENAME COLUMN id TO settings_id';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'settings' AND column_name = 'key'
  ) THEN
    EXECUTE 'ALTER TABLE finances.settings RENAME COLUMN key TO set_key';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'finances' AND table_name = 'settings' AND column_name = 'value'
  ) THEN
    EXECUTE 'ALTER TABLE finances.settings RENAME COLUMN value TO set_value';
  END IF;
END$$;
