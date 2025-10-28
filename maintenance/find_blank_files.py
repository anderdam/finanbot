from pathlib import Path
import re
import sys

ROOT = Path(".")
EXTS = {".py", ".sql", ".sh", ".md", ".yaml", ".yml", ".toml", ".txt", ".json"}


def is_blank_text(s: str) -> bool:
    # remove common comment styles and whitespace
    s2 = re.sub(r"(?m)^\s*(#|--|//).*$", "", s)  # strip line comments (#, --, //)
    s2 = re.sub(r"(?s)/\*.*?\*/", "", s2)  # strip block comments /* */
    return s2.strip() == ""


def main():
    zero = []
    blank = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if "__init__" in p.name or "__main__." in p.name:
            continue
        if p.stat().st_size == 0:
            zero.append(p)
            continue
        if p.suffix.lower() in EXTS:
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if is_blank_text(text):
                blank.append(p)
    if not zero and not blank:
        print("No zero-byte or blank files found.")
        return 0
    if zero:
        print("Zero-byte files:")
        for f in zero:
            print("  ", f)
    if blank:
        print("Files with only comments/whitespace:")
        for f in blank:
            print("  ", f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
