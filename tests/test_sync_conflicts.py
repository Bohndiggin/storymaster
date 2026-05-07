"""Tests for the conflict storage + resolution layer."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from storymaster.model.database.schema.base import (
    Actor,
    BaseTable,
    Setting,
    SyncConflict,
    User,
)
from storymaster.sync_client import conflicts as conflicts_api
from storymaster.sync_server.models import ConflictInfo, EntityChange
from storymaster.sync_server.sync_engine import SyncEngine


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    BaseTable.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    s = SessionLocal()
    yield s
    s.close()


@pytest.fixture
def setting(db):
    user = User(username="alice")
    db.add(user)
    db.commit()
    s = Setting(name="World", description="x", user_id=user.id)
    db.add(s)
    db.commit()
    return s


def _make_conflict_info(
    sync_uuid: str, mine: dict, theirs: dict, mv: int = 1, tv: int = 2
) -> ConflictInfo:
    return ConflictInfo(
        entity_type="actor",
        entity_id=1,
        sync_uuid=sync_uuid,
        mobile_version=mv,
        desktop_version=tv,
        mobile_updated_at=datetime.now(timezone.utc),
        desktop_updated_at=datetime.now(timezone.utc),
        mobile_data=mine,
        desktop_data=theirs,
        resolution="merge",
    )


def test_record_then_list(db, setting):
    actor = Actor(first_name="Local", setting_id=setting.id)
    db.add(actor)
    db.commit()

    info = _make_conflict_info(
        actor.sync_uuid,
        mine={"first_name": "Local", "setting_id_sync_uuid": setting.sync_uuid, "version": 1},
        theirs={"first_name": "Server", "setting_id_sync_uuid": setting.sync_uuid, "version": 2},
    )
    conflicts_api.record_conflict(db, info, source="push")

    pending = conflicts_api.list_pending(db)
    assert len(pending) == 1
    assert pending[0].entity_type == "actor"
    assert pending[0].target_sync_uuid == actor.sync_uuid


def test_record_dedupes_same_target(db, setting):
    actor = Actor(first_name="Local", setting_id=setting.id)
    db.add(actor)
    db.commit()

    info1 = _make_conflict_info(
        actor.sync_uuid,
        mine={"first_name": "v1", "setting_id_sync_uuid": setting.sync_uuid},
        theirs={"first_name": "server-v2", "setting_id_sync_uuid": setting.sync_uuid},
        mv=1, tv=2,
    )
    info2 = _make_conflict_info(
        actor.sync_uuid,
        mine={"first_name": "v1-edited", "setting_id_sync_uuid": setting.sync_uuid},
        theirs={"first_name": "server-v3", "setting_id_sync_uuid": setting.sync_uuid},
        mv=1, tv=3,
    )
    conflicts_api.record_conflict(db, info1, source="push")
    conflicts_api.record_conflict(db, info2, source="push")

    pending = conflicts_api.list_pending(db)
    assert len(pending) == 1  # second call updated, not appended
    assert pending[0].theirs_version == 3
    assert json.loads(pending[0].theirs_data)["first_name"] == "server-v3"


def test_resolve_use_theirs_overwrites_local(db, setting):
    actor = Actor(first_name="Mine", setting_id=setting.id)
    db.add(actor)
    db.commit()
    sync_uuid = actor.sync_uuid

    info = _make_conflict_info(
        sync_uuid,
        mine={"first_name": "Mine", "setting_id_sync_uuid": setting.sync_uuid, "version": 1},
        theirs={"first_name": "Theirs", "setting_id_sync_uuid": setting.sync_uuid, "version": 2},
        mv=1, tv=2,
    )
    c = conflicts_api.record_conflict(db, info, source="push")

    conflicts_api.resolve_use_theirs(db, c.id)

    db.refresh(actor)
    assert actor.first_name == "Theirs"
    assert actor.version == 2
    assert conflicts_api.list_pending(db) == []


def test_resolve_use_mine_keeps_local_bumps_version(db, setting):
    actor = Actor(first_name="MyEdit", setting_id=setting.id)
    db.add(actor)
    db.commit()
    sync_uuid = actor.sync_uuid

    info = _make_conflict_info(
        sync_uuid,
        mine={"first_name": "MyEdit", "setting_id_sync_uuid": setting.sync_uuid, "version": 1},
        theirs={"first_name": "Theirs", "setting_id_sync_uuid": setting.sync_uuid, "version": 2},
        mv=1, tv=2,
    )
    c = conflicts_api.record_conflict(db, info, source="push")

    conflicts_api.resolve_use_mine(db, c.id)

    db.refresh(actor)
    assert actor.first_name == "MyEdit"
    assert actor.version == 2  # bumped to theirs_version so next push lands


def test_resolve_with_merged(db, setting):
    actor = Actor(first_name="A", last_name="B", setting_id=setting.id)
    db.add(actor)
    db.commit()
    sync_uuid = actor.sync_uuid

    info = _make_conflict_info(
        sync_uuid,
        mine={
            "first_name": "Mine-First",
            "last_name": "Mine-Last",
            "setting_id_sync_uuid": setting.sync_uuid,
            "version": 1,
        },
        theirs={
            "first_name": "Theirs-First",
            "last_name": "Theirs-Last",
            "setting_id_sync_uuid": setting.sync_uuid,
            "version": 2,
        },
        mv=1, tv=2,
    )
    c = conflicts_api.record_conflict(db, info, source="push")

    merged = {
        "first_name": "Mine-First",       # mine wins for first
        "last_name": "Theirs-Last",       # theirs wins for last
        "setting_id_sync_uuid": setting.sync_uuid,
        "version": 2,
    }
    conflicts_api.resolve_with_merged(db, c.id, merged)

    db.refresh(actor)
    assert actor.first_name == "Mine-First"
    assert actor.last_name == "Theirs-Last"
    assert actor.version == 2


def test_discard_marks_resolved_no_data_change(db, setting):
    actor = Actor(first_name="Untouched", setting_id=setting.id)
    db.add(actor)
    db.commit()

    info = _make_conflict_info(
        actor.sync_uuid,
        mine={"first_name": "Untouched", "setting_id_sync_uuid": setting.sync_uuid, "version": 1},
        theirs={"first_name": "WhoCares", "setting_id_sync_uuid": setting.sync_uuid, "version": 2},
    )
    c = conflicts_api.record_conflict(db, info, source="push")

    conflicts_api.discard(db, c.id)

    db.refresh(actor)
    assert actor.first_name == "Untouched"
    assert actor.version == 1  # unchanged
    assert conflicts_api.list_pending(db) == []


def test_discard_all_clears_pending(db, setting):
    actor = Actor(first_name="A", setting_id=setting.id)
    db.add(actor)
    db.commit()
    for i in range(3):
        info = _make_conflict_info(
            actor.sync_uuid,
            mine={"first_name": f"m{i}", "setting_id_sync_uuid": setting.sync_uuid},
            theirs={"first_name": f"t{i}", "setting_id_sync_uuid": setting.sync_uuid},
            mv=1, tv=2 + i,
        )
        # Different sync_uuid each time so they don't dedupe
        info.sync_uuid = str(uuid.uuid4())
        conflicts_api.record_conflict(db, info, source="push")
    assert len(conflicts_api.list_pending(db)) == 3

    n = conflicts_api.discard_all(db)
    assert n == 3
    assert conflicts_api.list_pending(db) == []
    db.refresh(actor)
    assert actor.first_name == "A"  # not touched


def test_accept_all_incoming_applies_theirs_to_each(db, setting):
    a1 = Actor(first_name="LocalA", setting_id=setting.id)
    a2 = Actor(first_name="LocalB", setting_id=setting.id)
    db.add(a1)
    db.add(a2)
    db.commit()

    for actor, theirs_name in ((a1, "ServerA"), (a2, "ServerB")):
        info = _make_conflict_info(
            actor.sync_uuid,
            mine={
                "first_name": actor.first_name,
                "setting_id_sync_uuid": setting.sync_uuid,
                "version": 1,
            },
            theirs={
                "first_name": theirs_name,
                "setting_id_sync_uuid": setting.sync_uuid,
                "version": 2,
            },
            mv=1, tv=2,
        )
        conflicts_api.record_conflict(db, info, source="push")

    resolved, failed = conflicts_api.accept_all_incoming(db)
    assert resolved == 2
    assert failed == 0

    db.refresh(a1)
    db.refresh(a2)
    assert a1.first_name == "ServerA"
    assert a2.first_name == "ServerB"
    assert conflicts_api.list_pending(db) == []


def test_pull_records_conflicts(db, setting):
    """SyncEngine.apply_changes returns conflicts; sync_client should record them."""
    actor = Actor(first_name="LocalEdit", setting_id=setting.id)
    db.add(actor)
    db.commit()
    actor.version = 5
    db.commit()

    incoming = EntityChange(
        entity_type="actor",
        entity_id=999,
        sync_uuid=actor.sync_uuid,
        operation="update",
        entity_data={
            "first_name": "Stale",
            "setting_id_sync_uuid": setting.sync_uuid,
            "version": 2,
            "sync_uuid": actor.sync_uuid,
        },
        version=2,
        updated_at=datetime.now(timezone.utc),
    )
    engine = SyncEngine(db)
    result = engine.apply_changes(device=None, changes=[incoming], bump_versions=False)
    assert len(result["conflicts"]) == 1

    # Simulate what SyncClient.pull does:
    for c in result["conflicts"]:
        conflicts_api.record_conflict(db, c, source="pull")

    pending = conflicts_api.list_pending(db)
    assert len(pending) == 1
    assert pending[0].source == "pull"
    assert pending[0].mine_version == 5
    assert pending[0].theirs_version == 2
