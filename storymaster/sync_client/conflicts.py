"""Conflict storage and resolution.

When push or pull surfaces a version mismatch on a row, we don't silently
discard the loser. We record both sides as a SyncConflict row and let the
user decide later via the resolution dialog.

Resolution semantics — for any choice, we set the local row's version to
`theirs_version` so the next push reads `change.version=theirs_version`,
matches the server, and is accepted (then bumped to theirs_version+1):

  - "mine"     keep local data (already in the row), bump version
  - "theirs"   overwrite local data with theirs, bump version
  - "merged"   apply caller-supplied dict, bump version
  - "discard"  do nothing to the row, just mark resolved
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from storymaster.model.database.schema.base import SyncConflict
from storymaster.sync_server.models import ConflictInfo
from storymaster.sync_server.sync_engine import ENTITY_TYPE_MAP, SyncEngine

logger = logging.getLogger(__name__)


class ConflictResolutionError(Exception):
    """Raised when a resolution can't be applied (missing FK target, etc.)."""


def record_conflict(
    session: Session, conflict: ConflictInfo, source: str
) -> SyncConflict:
    """Persist a conflict for later UI review. `source` is 'push' or 'pull'."""
    if source not in {"push", "pull"}:
        raise ValueError(f"source must be 'push' or 'pull', got {source!r}")

    sync_uuid = conflict.sync_uuid
    if sync_uuid is None:
        # Older server responses might not include sync_uuid. Fall back to a
        # composite key so the UI still has something to display.
        sync_uuid = f"<unknown sync_uuid for {conflict.entity_type}#{conflict.entity_id}>"

    # Avoid duplicates: if there's already an unresolved conflict for the
    # same (entity_type, sync_uuid), update it rather than stacking up.
    existing = session.execute(
        select(SyncConflict).where(
            SyncConflict.entity_type == conflict.entity_type,
            SyncConflict.target_sync_uuid == sync_uuid,
            SyncConflict.resolved_at.is_(None),
        )
    ).scalar_one_or_none()

    # ConflictInfo is named from the *server's* perspective (mobile = the
    # pushing client, desktop = the server). On a push conflict, "we" are
    # mobile, so mine=mobile_data. On a pull conflict, the SyncEngine ran
    # locally with "we" as desktop, so mine=desktop_data.
    if source == "push":
        mine_data = conflict.mobile_data
        mine_version = conflict.mobile_version
        theirs_data = conflict.desktop_data
        theirs_version = conflict.desktop_version
    else:  # pull
        mine_data = conflict.desktop_data
        mine_version = conflict.desktop_version
        theirs_data = conflict.mobile_data
        theirs_version = conflict.mobile_version

    mine_json = json.dumps(mine_data) if mine_data else "{}"
    theirs_json = json.dumps(theirs_data) if theirs_data else "{}"

    if existing is not None:
        existing.mine_data = mine_json
        existing.theirs_data = theirs_json
        existing.mine_version = mine_version
        existing.theirs_version = theirs_version
        existing.source = source
        existing.detected_at = datetime.now(timezone.utc)
        session.commit()
        return existing

    row = SyncConflict(
        entity_type=conflict.entity_type,
        target_sync_uuid=sync_uuid,
        mine_data=mine_json,
        theirs_data=theirs_json,
        mine_version=mine_version,
        theirs_version=theirs_version,
        source=source,
        detected_at=datetime.now(timezone.utc),
    )
    session.add(row)
    session.commit()
    return row


def list_pending(session: Session) -> list[SyncConflict]:
    return list(
        session.execute(
            select(SyncConflict)
            .where(SyncConflict.resolved_at.is_(None))
            .order_by(SyncConflict.detected_at.desc())
        ).scalars()
    )


def count_pending(session: Session) -> int:
    return (
        session.execute(
            select(SyncConflict).where(SyncConflict.resolved_at.is_(None))
        )
        .scalars()
        .all()
        .__len__()
    )


def resolve_use_mine(session: Session, conflict_id: int) -> None:
    """Keep local data, bump version so next push lands."""
    conflict = _load(session, conflict_id)
    row = _find_target_row(session, conflict)
    if row is not None:
        row.version = conflict.theirs_version
    _mark_resolved(session, conflict, "mine")


def resolve_use_theirs(session: Session, conflict_id: int) -> None:
    """Overwrite local with theirs (FK-translated), bump version."""
    conflict = _load(session, conflict_id)
    theirs = json.loads(conflict.theirs_data)
    _apply_data_to_row(session, conflict, theirs)
    _mark_resolved(session, conflict, "theirs")


def resolve_with_merged(
    session: Session, conflict_id: int, merged: dict[str, Any]
) -> None:
    """Apply a caller-built merged dict (typically per-field picks)."""
    conflict = _load(session, conflict_id)
    _apply_data_to_row(session, conflict, merged)
    _mark_resolved(session, conflict, "merged")


def discard(session: Session, conflict_id: int) -> None:
    """Mark resolved without changing the local row."""
    conflict = _load(session, conflict_id)
    _mark_resolved(session, conflict, "discarded")


def discard_all(session: Session) -> int:
    """Mark every pending conflict as discarded. Returns count discarded.

    Does not change any entity rows — only the SyncConflict ledger. Useful
    when a software bug created spurious conflicts and you want a clean slate.
    """
    pending = list_pending(session)
    now = datetime.now(timezone.utc)
    for c in pending:
        c.resolution = "discarded"
        c.resolved_at = now
    session.commit()
    return len(pending)


def accept_all_incoming(session: Session) -> tuple[int, int]:
    """Apply 'theirs' to every pending conflict. Returns (resolved, failed).

    Best-effort: if one conflict can't be applied (missing FK target etc.),
    log it and keep going on the rest. The failed ones stay pending for the
    user to inspect manually.
    """
    pending = list_pending(session)
    resolved = 0
    failed = 0
    for c in pending:
        try:
            resolve_use_theirs(session, c.id)
            resolved += 1
        except ConflictResolutionError as e:
            logger.warning(
                "Could not auto-accept conflict id=%s (%s sync_uuid=%s): %s",
                c.id, c.entity_type, c.target_sync_uuid, e,
            )
            failed += 1
            # resolve_use_theirs raises before commit on failure, but the
            # session may need a clean state for the next iteration.
            try:
                session.rollback()
            except Exception:
                pass
    return resolved, failed


# ---- internals ----


def _load(session: Session, conflict_id: int) -> SyncConflict:
    conflict = session.get(SyncConflict, conflict_id)
    if conflict is None:
        raise ConflictResolutionError(f"No conflict with id={conflict_id}")
    if conflict.resolved_at is not None:
        raise ConflictResolutionError(f"Conflict {conflict_id} already resolved")
    return conflict


def _find_target_row(session: Session, conflict: SyncConflict):
    model = ENTITY_TYPE_MAP.get(conflict.entity_type)
    if model is None:
        return None
    return session.execute(
        select(model).where(model.sync_uuid == conflict.target_sync_uuid)
    ).scalar_one_or_none()


def _apply_data_to_row(
    session: Session, conflict: SyncConflict, data: dict[str, Any]
) -> None:
    """Apply `data` to the row identified by the conflict, FK-translating."""
    model = ENTITY_TYPE_MAP.get(conflict.entity_type)
    if model is None:
        raise ConflictResolutionError(
            f"Unknown entity type: {conflict.entity_type}"
        )
    row = _find_target_row(session, conflict)

    engine = SyncEngine(session)
    translated, missing = engine._resolve_fk_uuids_to_local_ids(model, data)
    if missing:
        raise ConflictResolutionError(
            f"Cannot apply: missing FK targets {missing}. "
            "Pull again to fetch them, then retry."
        )

    if row is None:
        # Local row was deleted while a conflict was outstanding. Re-create.
        clean = {
            k: engine._convert_value_for_column(model, k, v)
            for k, v in translated.items()
            if k != "id"
        }
        clean["sync_uuid"] = conflict.target_sync_uuid
        clean["version"] = conflict.theirs_version
        row = model(**clean)
        session.add(row)
        return

    for key, value in translated.items():
        if key in {"id", "sync_uuid"}:
            continue
        if hasattr(row, key):
            converted = engine._convert_value_for_column(model, key, value)
            setattr(row, key, converted)
    row.version = conflict.theirs_version


def _mark_resolved(session: Session, conflict: SyncConflict, resolution: str) -> None:
    conflict.resolution = resolution
    conflict.resolved_at = datetime.now(timezone.utc)
    session.commit()
