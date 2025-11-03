import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from src.core.config import get_settings

settings = get_settings()


def backup_database() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"db_backup_{timestamp}.sql"
    backup_path = Path(settings.backup_dir) / filename

    cmd = [
        "pg_dump",
        "-h",
        settings.postgres_host,
        "-p",
        settings.postgres_port,
        "-U",
        settings.postgres_user,
        "-d",
        settings.postgres_db,
        "-n",
        settings.schema,
        "-f",
        str(backup_path),
    ]

    env = {"PGPASSWORD": settings.postgres_password}
    subprocess.run(cmd, env=env, check=True)
    return backup_path


def backup_attachments() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"attachments_{timestamp}.zip"
    archive_path = Path(settings.backup_dir) / archive_name

    shutil.make_archive(
        base_name=str(archive_path).replace(".zip", ""),
        format="zip",
        root_dir=settings.attachments_dir,
    )
    return archive_path


def run_backup() -> tuple[Path, Path]:
    db_path = backup_database()
    attachments_path = backup_attachments()
    return db_path, attachments_path
