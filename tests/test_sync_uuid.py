"""Tests for sync_uuid-based upsert and FK translation in the sync engine."""

import uuid

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from storymaster.model.database.schema.base import (
    Actor,
    BaseTable,
    Setting,
    SyncDevice,
    User,
)
from storymaster.sync_server.models import EntityChange
from storymaster.sync_server.sync_engine import SyncEngine


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    BaseTable.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def device(db):
    d = SyncDevice(
        device_id="test-device", device_name="Test Device", auth_token="t"
    )
    db.add(d)
    db.commit()
    return d


@pytest.fixture
def user(db):
    u = User(username="alice")
    db.add(u)
    db.commit()
    return u


@pytest.fixture
def setting(db, user):
    s = Setting(name="Test World", description="…", user_id=user.id)
    db.add(s)
    db.commit()
    return s


def test_sync_uuid_auto_assigned_on_insert(db, user):
    s = Setting(name="World", description="x", user_id=user.id)
    db.add(s)
    db.commit()
    assert s.sync_uuid is not None
    # Valid UUID4 string
    uuid.UUID(s.sync_uuid)


def test_upsert_creates_when_missing(db, device, setting):
    """A push for an unknown sync_uuid should insert a new row locally."""
    incoming_uuid = str(uuid.uuid4())
    change = EntityChange(
        entity_type="actor",
        entity_id=999,  # sender's local id — we ignore it
        sync_uuid=incoming_uuid,
        operation="create",
        entity_data={
            "id": 999,
            "first_name": "Bob",
            "last_name": "Smith",
            "setting_id": 999,  # sender's local id, irrelevant
            "setting_id_sync_uuid": setting.sync_uuid,  # canonical reference
            "sync_uuid": incoming_uuid,
            "version": 1,
        },
        version=1,
        updated_at=None,
    )
    engine = SyncEngine(db)
    result = engine.apply_changes(device, [change])
    assert result["accepted"] == 1
    assert result["rejected"] == 0
    # Row exists with the incoming sync_uuid and FK resolved to local setting.id
    row = db.execute(
        select(Actor).where(Actor.sync_uuid == incoming_uuid)
    ).scalar_one()
    assert row.first_name == "Bob"
    assert row.setting_id == setting.id  # translated, not 999


def test_upsert_updates_when_present(db, device, setting):
    """A push with a known sync_uuid should update in place via version check."""
    actor = Actor(first_name="Old", setting_id=setting.id)
    db.add(actor)
    db.commit()
    baseline_version = actor.version
    canonical_uuid = actor.sync_uuid
    local_id = actor.id

    change = EntityChange(
        entity_type="actor",
        entity_id=999,
        sync_uuid=canonical_uuid,
        operation="update",
        entity_data={
            "first_name": "New",
            "setting_id_sync_uuid": setting.sync_uuid,
            "version": baseline_version,
            "sync_uuid": canonical_uuid,
        },
        version=baseline_version,
        updated_at=None,
    )
    engine = SyncEngine(db)
    result = engine.apply_changes(device, [change])
    assert result["accepted"] == 1
    db.refresh(actor)
    assert actor.id == local_id  # unchanged
    assert actor.first_name == "New"
    assert actor.version == baseline_version + 1


def test_upsert_version_conflict(db, device, setting):
    """If local version > incoming, return a conflict, not an update."""
    actor = Actor(first_name="Local Edit", setting_id=setting.id)
    db.add(actor)
    db.commit()
    actor.version = 5
    db.commit()

    change = EntityChange(
        entity_type="actor",
        entity_id=999,
        sync_uuid=actor.sync_uuid,
        operation="update",
        entity_data={
            "first_name": "Stale Push",
            "setting_id_sync_uuid": setting.sync_uuid,
            "version": 2,  # stale
            "sync_uuid": actor.sync_uuid,
        },
        version=2,
        updated_at=None,
    )
    engine = SyncEngine(db)
    result = engine.apply_changes(device, [change])
    assert result["accepted"] == 0
    assert len(result["conflicts"]) == 1
    db.refresh(actor)
    assert actor.first_name == "Local Edit"  # unchanged


def test_fk_target_missing_rejects(db, device):
    """Push referencing an unknown FK sync_uuid should be rejected (sender retries)."""
    change = EntityChange(
        entity_type="actor",
        entity_id=1,
        sync_uuid=str(uuid.uuid4()),
        operation="create",
        entity_data={
            "first_name": "Orphan",
            "setting_id_sync_uuid": str(uuid.uuid4()),  # not present locally
            "version": 1,
            "sync_uuid": "doesnt-matter",
        },
        version=1,
        updated_at=None,
    )
    engine = SyncEngine(db)
    result = engine.apply_changes(device, [change])
    assert result["accepted"] == 0
    assert result["rejected"] == 1


def test_pull_includes_fk_sync_uuids(db, setting):
    """get_changes_since should attach <fk>_sync_uuid alongside the local FK id."""
    actor = Actor(first_name="A", setting_id=setting.id)
    db.add(actor)
    db.commit()

    engine = SyncEngine(db)
    changes = engine.get_changes_since(
        since_timestamp=None, entity_types=["actor"]
    )
    actor_change = next(c for c in changes if c.sync_uuid == actor.sync_uuid)
    assert actor_change.data["setting_id"] == setting.id
    assert actor_change.data["setting_id_sync_uuid"] == setting.sync_uuid


def test_delete_by_sync_uuid(db, device, setting):
    actor = Actor(first_name="Doomed", setting_id=setting.id)
    db.add(actor)
    db.commit()
    canonical_uuid = actor.sync_uuid

    change = EntityChange(
        entity_type="actor",
        entity_id=actor.id,
        sync_uuid=canonical_uuid,
        operation="delete",
        entity_data=None,
        version=actor.version,
        updated_at=None,
    )
    engine = SyncEngine(db)
    result = engine.apply_changes(device, [change])
    assert result["accepted"] == 1
    db.refresh(actor)
    assert actor.deleted_at is not None
