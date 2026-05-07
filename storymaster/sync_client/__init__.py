"""Storymaster desktop sync client.

Talks to a self-hosted sync server so multiple desktops can share a single
canonical database while keeping local SQLite for offline work.
"""

from storymaster.sync_client.client import SyncClient
from storymaster.sync_client.config import SyncClientConfig, load_config, save_config

__all__ = ["SyncClient", "SyncClientConfig", "load_config", "save_config"]
