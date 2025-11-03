#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

# Optional: load .env if python-dotenv is available, but avoid hard dependency
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # fallback: try basic .env loader
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                os.environ.setdefault(k, v)

REQUIRED = [
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "SECRET_KEY",
]

missing = [k for k in REQUIRED if not os.environ.get(k)]
if missing:
    print(
        "ERROR: Missing required environment variables: " + ", ".join(missing),
        file=sys.stderr,
    )
    sys.exit(1)

# SECRET_KEY length
if len(os.environ["SECRET_KEY"]) < 16:
    print(
        f"ERROR: SECRET_KEY must be at least 16 characters long "
        f"(current: {len(os.environ['SECRET_KEY'])})",
        file=sys.stderr,
    )
    sys.exit(2)

# PORT validation
try:
    port = int(os.environ.get("POSTGRES_PORT", "0"))
except ValueError:
    print(
        f"ERROR: POSTGRES_PORT must be an integer, "
        f"got '{os.environ.get('POSTGRES_PORT')}'",
        file=sys.stderr,
    )
    sys.exit(3)
if not (0 < port < 65536):
    print(
        f"ERROR: POSTGRES_PORT must be between 1 and 65535, got {port}", file=sys.stderr
    )
    sys.exit(4)

# Build DATABASE_URL if missing
if not os.environ.get("DATABASE_URL"):
    enc = quote_plus(os.environ["POSTGRES_PASSWORD"])
    os.environ["DATABASE_URL"] = (
        f"postgresql://{os.environ['POSTGRES_USER']}:{enc}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
    )
    print("INFO: Built DATABASE_URL from components.")

# Ensure attachments dir exists and writable
attachments_dir = os.environ.get("ATTACHMENTS_DIR")
if attachments_dir:
    p = Path(attachments_dir)
    p.mkdir(parents=True, exist_ok=True)
    test_file = p / (".permtest_" + os.urandom(6).hex())
    try:
        test_file.write_bytes(b"ok")
        test_file.unlink()
    except Exception as exc:
        print(
            f"ERROR: ATTACHMENTS_DIR '{attachments_dir}' is not writable: {exc}",
            file=sys.stderr,
        )
        sys.exit(5)

# Ensure command provided
if len(sys.argv) <= 1:
    print(
        "ERROR: No command provided to start. Usage: ensure_env_and_start.py "
        "<cmd> [args...]",
        file=sys.stderr,
    )
    sys.exit(6)

cmd = sys.argv[1:]
print("DEBUG ENV:")
for k in (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_USER",
    "POSTGRES_DB",
    "SECRET_KEY",
    "LOG_LEVEL",
    "DATABASE_URL",
):
    print(k, "=", os.environ.get(k))

print("Environment validated. Executing:", " ".join(cmd))
# Replace the current process with the requested command
os.execvp(cmd[0], cmd)
