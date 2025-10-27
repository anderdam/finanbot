"""Rename DB columns to new conventions (id -> <table>_id,
name/type/key/value -> prefixed).
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_rename_columns"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename only when the old column exists. Keeps operation idempotent.
    op.execute(
        """
DO $$
BEGIN
  -- users.users_id -> users_id
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
                 AND table_name = 'users'
                 AND column_name = 'id') THEN
    EXECUTE 'ALTER TABLE finances.users
        RENAME COLUMN id TO users_id';
  END IF;

  -- accounts.accounts_id, accounts.acc_name, accounts.acc_type
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
                AND table_name = 'accounts'
                AND column_name = 'id') THEN
    EXECUTE 'ALTER TABLE finances.accounts
        RENAME COLUMN id TO accounts_id';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
                AND table_name = 'accounts'
                AND column_name = 'name') THEN
    EXECUTE 'ALTER TABLE finances.accounts
        RENAME COLUMN name TO acc_name';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
                AND table_name = 'accounts'
                AND column_name = 'type') THEN
    EXECUTE 'ALTER TABLE finances.accounts
        RENAME COLUMN type TO acc_type';
  END IF;

  -- categories.categories_id, categories.cat_name
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
                AND table_name = 'categories'
                AND column_name = 'id') THEN
    EXECUTE 'ALTER TABLE finances.categories
        RENAME COLUMN id TO categories_id';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'categories'
             AND column_name = 'name') THEN
    EXECUTE 'ALTER TABLE finances.categories
        RENAME COLUMN name TO cat_name';
  END IF;

  -- transactions.transactions_id, transactions.tra_type
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'transactions'
             AND column_name = 'id') THEN
    EXECUTE 'ALTER TABLE finances.transactions
        RENAME COLUMN id TO transactions_id';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'transactions'
             AND column_name = 'type') THEN
    EXECUTE 'ALTER TABLE finances.transactions
        RENAME COLUMN type TO tra_type';
  END IF;

  -- settings.settings_id, settings.set_key, settings.set_value
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'settings'
             AND column_name = 'id') THEN
    EXECUTE 'ALTER TABLE finances.settings
        RENAME COLUMN id TO settings_id';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'settings'
             AND column_name = 'key') THEN
    EXECUTE 'ALTER TABLE finances.settings
        RENAME COLUMN key TO set_key';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'settings'
             AND column_name = 'value') THEN
    EXECUTE 'ALTER TABLE finances.settings
        RENAME COLUMN value TO set_value';
  END IF;
END
$$;
"""
    )


def downgrade() -> None:
    # Reverse renames only if prefixed column exists
    op.execute(
        """
DO $$
BEGIN
  -- users_id -> id
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'users'
             AND column_name = 'users_id') THEN
    EXECUTE 'ALTER TABLE finances.users
        RENAME COLUMN users_id TO id';
  END IF;

  -- accounts
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances' AND
            table_name = 'accounts'
            AND column_name = 'accounts_id') THEN
    EXECUTE 'ALTER TABLE finances.accounts
        RENAME COLUMN accounts_id TO id';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'accounts'
             AND column_name = 'acc_name') THEN
    EXECUTE 'ALTER TABLE finances.accounts
        RENAME COLUMN acc_name TO name';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'accounts'
             AND column_name = 'acc_type') THEN
    EXECUTE 'ALTER TABLE finances.accounts RENAME COLUMN acc_type TO type';
  END IF;

  -- categories
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'categories'
             AND column_name = 'categories_id') THEN
    EXECUTE 'ALTER TABLE finances.categories RENAME COLUMN categories_id TO id';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'categories'
             AND column_name = 'cat_name') THEN
    EXECUTE 'ALTER TABLE finances.categories RENAME COLUMN cat_name TO name';
  END IF;

  -- transactions
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'transactions'
             AND column_name = 'transactions_id') THEN
    EXECUTE 'ALTER TABLE finances.transactions RENAME COLUMN transactions_id TO id';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'transactions'
             AND column_name = 'tra_type') THEN
    EXECUTE 'ALTER TABLE finances.transactions RENAME COLUMN tra_type TO type';
  END IF;

  -- settings
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'settings'
             AND column_name = 'settings_id') THEN
    EXECUTE 'ALTER TABLE finances.settings RENAME COLUMN settings_id TO id';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'settings'
             AND column_name = 'set_key') THEN
    EXECUTE 'ALTER TABLE finances.settings RENAME COLUMN set_key TO key';
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_schema = 'finances'
             AND table_name = 'settings'
             AND column_name = 'set_value') THEN
    EXECUTE 'ALTER TABLE finances.settings RENAME COLUMN set_value TO value';
  END IF;
END
$$;
"""
    )
