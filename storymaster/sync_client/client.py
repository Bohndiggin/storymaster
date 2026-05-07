"""SyncClient — desktop-side counterpart to the sync server."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from storymaster.sync_client.config import (
    SyncClientConfig,
    load_config,
    save_config,
)
from storymaster.sync_server.models import EntityChange
from storymaster.sync_server.sync_engine import SyncEngine

logger = logging.getLogger(__name__)


class SyncError(Exception):
    """Raised when sync fails for a recoverable reason (network, auth, etc.)."""


class SyncClient:
    """
    Drives pull/push against a remote Storymaster sync server.

    Sessions are short-lived and committed inside the engine; we open a fresh
    SQLAlchemy session per operation to avoid stepping on the desktop app's
    long-lived sessions.
    """

    PULL_PATH = "/api/sync/pull"
    PUSH_PATH = "/api/sync/push"
    REGISTER_PATH = "/api/pair/register"

    def __init__(
        self,
        config: Optional[SyncClientConfig] = None,
        timeout: int = 30,
        engine: Optional[Engine] = None,
    ):
        self.config = config or load_config()
        self.timeout = timeout
        if engine is None:
            # Imported lazily so importing sync_client doesn't force the local
            # DB engine to spin up (helpful for tests and tooling).
            from storymaster.model.database.base_connection import engine as local_engine
            engine = local_engine
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

    # ---- public API ----

    def is_configured(self) -> bool:
        return self.config.is_paired

    def pair(self, server_url: str, pairing_token: str, device_name: Optional[str] = None) -> None:
        """Register this device with the server and persist the resulting auth token."""
        url = server_url.rstrip("/") + self.REGISTER_PATH
        payload = {
            "device_id": self.config.device_id,
            "device_name": device_name or self.config.device_name,
            "pairing_token": pairing_token,
        }
        try:
            r = requests.post(url, json=payload, timeout=self.timeout)
        except requests.RequestException as e:
            raise SyncError(f"Network error during pairing: {e}") from e

        if r.status_code != 200:
            raise SyncError(f"Pairing failed ({r.status_code}): {r.text}")

        body = r.json()
        self.config.server_url = server_url.rstrip("/")
        self.config.auth_token = body["auth_token"]
        if device_name:
            self.config.device_name = device_name
        save_config(self.config)

    def sync_now(self) -> dict:
        """Push then pull. Returns a summary dict for status display."""
        push_summary = self.push()
        pull_summary = self.pull()
        return {"push": push_summary, "pull": pull_summary}

    def pull(self) -> dict:
        """Pull changes from the server and apply them to the local DB."""
        if not self.config.is_paired:
            raise SyncError("Not paired with a server")

        body = {
            "since_timestamp": self.config.last_pulled_at,
            "entity_types": None,
        }
        url = self.config.server_url + self.PULL_PATH
        r = self._post(url, json=body)
        payload = r.json()

        # Re-parse changes through the Pydantic model so types align.
        changes = [EntityChange.model_validate(c) for c in payload.get("changes", [])]

        applied = {"accepted": 0, "rejected": 0, "conflicts": 0}
        if changes:
            with self._session() as session:
                local = SyncEngine(session)
                result = local.apply_changes(
                    device=None,  # client side: no SyncLog row
                    changes=changes,
                    bump_versions=False,  # mirror server's authoritative versions
                )
                applied = {
                    "accepted": result["accepted"],
                    "rejected": result["rejected"],
                    "conflicts": len(result["conflicts"]),
                }

        # Use the server's sync_timestamp as the new high-water mark.
        server_ts = payload.get("sync_timestamp")
        if server_ts:
            self.config.last_pulled_at = server_ts
            save_config(self.config)

        logger.info("Pull: %s", applied)
        return applied

    def push(self) -> dict:
        """Send local changes since last push to the server."""
        if not self.config.is_paired:
            raise SyncError("Not paired with a server")

        with self._session() as session:
            local = SyncEngine(session)
            since = self.config.last_pushed_at_dt
            changes = local.get_changes_since(since_timestamp=since)

        if not changes:
            self.config.last_pushed_at = datetime.now(timezone.utc).isoformat()
            save_config(self.config)
            return {"sent": 0, "accepted": 0, "rejected": 0, "conflicts": 0}

        url = self.config.server_url + self.PUSH_PATH
        # Pydantic .model_dump() with mode='json' produces JSON-serializable types.
        body = {"changes": [c.model_dump(mode="json", by_alias=False) for c in changes]}
        r = self._post(url, json=body)
        payload = r.json()

        summary = {
            "sent": len(changes),
            "accepted": payload.get("accepted", 0),
            "rejected": payload.get("rejected", 0),
            "conflicts": len(payload.get("conflicts", [])),
        }

        # Only advance the watermark if everything was accepted, otherwise we
        # need the rejected rows to be considered again next push.
        if summary["rejected"] == 0 and summary["conflicts"] == 0:
            self.config.last_pushed_at = datetime.now(timezone.utc).isoformat()
            save_config(self.config)

        logger.info("Push: %s", summary)
        return summary

    # ---- internals ----

    def _post(self, url: str, *, json: dict) -> requests.Response:
        headers = {"Authorization": f"Bearer {self.config.auth_token}"}
        try:
            r = requests.post(url, json=json, headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise SyncError(f"Network error: {e}") from e
        if r.status_code == 401:
            raise SyncError("Unauthorized — auth token may have been revoked")
        if r.status_code >= 400:
            raise SyncError(f"Server error ({r.status_code}): {r.text}")
        return r

    def _session(self) -> "_SessionContext":
        return _SessionContext(self._session_factory)


class _SessionContext:
    """Context-managed SQLAlchemy session for the local DB."""

    def __init__(self, factory):
        self._factory = factory
        self._session: Optional[Session] = None

    def __enter__(self) -> Session:
        self._session = self._factory()
        return self._session

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._session is None:
            return
        try:
            if exc is not None:
                self._session.rollback()
        finally:
            self._session.close()
