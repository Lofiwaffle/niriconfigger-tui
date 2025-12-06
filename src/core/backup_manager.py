"""Backup and restore management for configuration files."""

from pathlib import Path
from datetime import datetime
from typing import Optional
import shutil


class BackupManager:
    """Manages configuration backups."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize backup manager.

        Args:
            config_path: Path to config.kdl (default: ~/.config/niri/config.kdl)
        """
        if config_path is None:
            config_path = Path.home() / ".config" / "niri" / "config.kdl"

        self.config_path = Path(config_path)
        self.backup_dir = self.config_path.parent / "backups"

        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Path:
        """Create a timestamped backup of current configuration.

        Returns:
            Path to the created backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"config-{timestamp}.kdl"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(self.config_path, backup_path)
        return backup_path

    def get_latest_backup(self) -> Optional[Path]:
        """Get the most recent backup file.

        Returns:
            Path to latest backup or None if no backups exist
        """
        if not self.backup_dir.exists():
            return None

        backups = sorted(
            self.backup_dir.glob("config-*.kdl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        return backups[0] if backups else None

    def get_backups(self, limit: int = 10) -> list:
        """Get list of recent backups.

        Args:
            limit: Maximum number of backups to return

        Returns:
            List of backup paths sorted by date (newest first)
        """
        if not self.backup_dir.exists():
            return []

        backups = sorted(
            self.backup_dir.glob("config-*.kdl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        return backups[:limit]

    def restore(self, backup_path: Path) -> bool:
        """Restore configuration from a backup.

        Args:
            backup_path: Path to backup file to restore

        Returns:
            True if successful

        Raises:
            FileNotFoundError: If backup doesn't exist
            IOError: If restore fails
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        shutil.copy2(backup_path, self.config_path)
        return True

    def delete_backup(self, backup_path: Path) -> bool:
        """Delete a backup file.

        Args:
            backup_path: Path to backup to delete

        Returns:
            True if successful
        """
        if backup_path.exists():
            backup_path.unlink()
        return True

    def cleanup_old_backups(self, keep: int = 20) -> int:
        """Delete old backups, keeping only the most recent ones.

        Args:
            keep: Number of backups to keep

        Returns:
            Number of deleted backups
        """
        if not self.backup_dir.exists():
            return 0

        backups = sorted(
            self.backup_dir.glob("config-*.kdl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        deleted = 0
        for backup in backups[keep:]:
            backup.unlink()
            deleted += 1

        return deleted
