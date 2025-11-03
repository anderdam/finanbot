from pathlib import Path
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class FilesystemConfig(BaseSettings):
    attachments_dir: Path = Field(Path("/data/attachments"), env="ATTACHMENTS_DIR")
    backup_dir: Path = Field(Path("/data/backups"), env="BACKUP_DIR")

    @computed_field
    def attachments_path(self) -> Path:
        return self.attachments_dir.expanduser().resolve()

    @computed_field
    def backup_path(self) -> Path:
        return self.backup_dir.expanduser().resolve()
