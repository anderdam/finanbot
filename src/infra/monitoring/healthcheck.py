import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / "backup" / ".env")


def check_db():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", 5432),
        )
        conn.close()
        return True
    except Exception as e:
        print(f"❌ DB check failed: {e}")
        return False


def check_fs():
    try:
        test_path = Path(os.getenv("ATTACHMENTS_DIR", "/tmp")) / "healthcheck.tmp"
        with open(test_path, "w") as f:
            f.write("ok")
        test_path.unlink()
        return True
    except Exception as e:
        print(f"❌ Filesystem check failed: {e}")
        return False


if __name__ == "__main__":
    db_ok = check_db()
    fs_ok = check_fs()

    print(f"DB OK: {db_ok}")
    print(f"FS OK: {fs_ok}")

    if db_ok and fs_ok:
        exit(0)
    else:
        exit(1)
