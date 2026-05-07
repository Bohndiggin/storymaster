"""Persistent sync client configuration.

Stored at ~/.config/storymaster/sync.json. Holds the remote server URL, the
auth token issued during pairing, this device's identity, and watermarks for
the last successful pull/push.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


def _config_dir() -> Path:
    home = Path(os.path.expanduser("~"))
    return home / ".config" / "storymaster"


def _config_path() -> Path:
    return _config_dir() / "sync.json"


@dataclass
class SyncClientConfig:
    server_url: Optional[str] = None
    auth_token: Optional[str] = None
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_name: str = field(default_factory=lambda: os.uname().nodename if hasattr(os, "uname") else "desktop")
    last_pulled_at: Optional[str] = None  # ISO8601 string from server
    last_pushed_at: Optional[str] = None  # ISO8601 string

    @property
    def is_paired(self) -> bool:
        return bool(self.server_url) and bool(self.auth_token)

    @property
    def last_pulled_at_dt(self) -> Optional[datetime]:
        return datetime.fromisoformat(self.last_pulled_at) if self.last_pulled_at else None

    @property
    def last_pushed_at_dt(self) -> Optional[datetime]:
        return datetime.fromisoformat(self.last_pushed_at) if self.last_pushed_at else None


def load_config() -> SyncClientConfig:
    path = _config_path()
    if not path.exists():
        return SyncClientConfig()
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return SyncClientConfig()
    # Keep only known fields so old/extra keys don't crash dataclass init.
    known = {f for f in SyncClientConfig.__dataclass_fields__}
    filtered = {k: v for k, v in data.items() if k in known}
    return SyncClientConfig(**filtered)


def save_config(config: SyncClientConfig) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Restrict perms — auth token is sensitive.
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(asdict(config), indent=2))
    os.chmod(tmp, 0o600)
    tmp.replace(path)
