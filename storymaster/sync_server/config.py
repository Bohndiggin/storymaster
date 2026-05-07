"""Configuration for the Storymaster Sync Server"""

import os
from pathlib import Path


class SyncServerConfig:
    """Configuration settings for the sync server"""

    # Server settings
    HOST: str = "0.0.0.0"  # Listen on all interfaces for mobile access
    PORT: int = 8765
    RELOAD: bool = False  # Set to True for development

    # CORS settings - allow mobile app to connect
    CORS_ORIGINS: list[str] = ["*"]  # In production, specify mobile app URL
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    # Database settings
    @staticmethod
    def get_database_path() -> str:
        """Get the path to the Storymaster database"""
        # Allow override for self-hosted deployments.
        env_path = os.getenv("STORYMASTER_DB_PATH")
        if env_path:
            return env_path
        home_dir = os.path.expanduser("~")
        db_dir = os.path.join(home_dir, ".local", "share", "storymaster")
        db_path = os.path.join(db_dir, "storymaster.db")
        return db_path

    @staticmethod
    def get_database_url() -> str:
        """Get SQLAlchemy database URL.

        Honors STORYMASTER_DB_URL (full SQLAlchemy URL) first, then
        STORYMASTER_DB_PATH (SQLite file path), finally the default user-local file.
        """
        env_url = os.getenv("STORYMASTER_DB_URL")
        if env_url:
            return env_url
        db_path = SyncServerConfig.get_database_path()
        return f"sqlite:///{db_path}"

    # Security settings
    TOKEN_EXPIRY_HOURS: int = 24 * 365  # 1 year - tokens don't expire frequently
    SECRET_KEY: str = os.getenv("SYNC_SECRET_KEY", "change-this-in-production")

    # Sync settings
    MAX_SYNC_BATCH_SIZE: int = 1000  # Maximum entities per sync batch
    CONFLICT_RESOLUTION_MODE: str = "version"  # "version" or "timestamp"


# Global config instance
config = SyncServerConfig()
