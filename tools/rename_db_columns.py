# #!/usr/bin/env python3
"""
Scan project files and replace legacy DB column identifiers with new names.
Creates a .bak backup for each modified file.

Run from repo root:
    python tools/rename_db_columns.py

Adjust PATHS if needed.
"""

from pathlib import Path
import re
import shutil

# mapping: old -> new (word-boundary aware)
REPLACEMENTS = {
    # users
    r"\busers\.id\b": "users.users_id",
    r"\bfinances\.users\.id\b": "finances.users.users_id",
    # no-op safe fallback (keeps mapping consistent)
    r"\b\\busers_id\\b": "users.users_id",
    # accounts
    r"\baccounts\.id\b": "accounts.accounts_id",
    r"\baccounts\.name\b": "accounts.acc_name",
    r"\baccounts\.type\b": "accounts.acc_type",
    r"\bfinances\.accounts\.id\b": "finances.accounts.accounts_id",
    # categories
    r"\bcategories\.id\b": "categories.categories_id",
    r"\bcategories\.name\b": "categories.cat_name",
    r"\bfinances\.categories\.id\b": "finances.categories.categories_id",
    # transactions
    r"\btransactions\.id\b": "transactions.transactions_id",
    r"\btransactions\.type\b": "transactions.tra_type",
    r"\bfinances\.transactions\.id\b": "finances.transactions.transactions_id",
    # settings
    r"\bsettings\.id\b": "settings.settings_id",
    r"\bsettings\.key\b": "settings.set_key",
    r"\bsettings\.value\b": "settings.set_value",
    r"\bfinances\.settings\.id\b": "finances.settings.settings_id",
}

# File globs to update
SOURCE_DIRS = ["src", "tests", "ui", "src/finanbot/db"]


def replace_in_file(path: Path, patterns):
    text = path.read_text(encoding="utf-8")
    new_text = text
    for patt, repl in patterns.items():
        new_text = re.sub(patt, repl, new_text)
    if new_text != text:
        bak = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, bak)
        path.write_text(new_text, encoding="utf-8")
        print(f"Updated {path} (backup -> {bak})")


def main():
    # patterns = {re.compile(k): v for k, v in REPLACEMENTS.items()}
    files = []
    for d in SOURCE_DIRS:
        p = Path(d)
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if f.is_file() and f.suffix in {
                ".py",
                ".sql",
                ".yaml",
                ".yml",
                ".md",
                ".txt",
            }:
                files.append(f)

    for f in files:
        text = f.read_text(encoding="utf-8")
        new_text = text
        for k, v in REPLACEMENTS.items():
            new_text = re.sub(k, v, new_text)
        if new_text != text:
            bak = f.with_suffix(f.suffix + ".bak")
            shutil.copy2(f, bak)
            f.write_text(new_text, encoding="utf-8")
            print(f"Patched {f} -> backup saved to {bak}")

    print("Done. Verify changes, run tests, then commit.")


if __name__ == "__main__":
    main()
