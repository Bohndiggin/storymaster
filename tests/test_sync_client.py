"""End-to-end test: SyncClient pulls/pushes against an in-process server."""

from __future__ import annotations

import threading
import time
import uuid
from contextlib import contextmanager
from wsgiref.simple_server import make_server

import pytest
import uvicorn
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from storymaster.model.database.schema.base import (
    Actor,
    BaseTable,
    Setting,
    SyncDevice,
    User,
)
from storymaster.sync_client.client import SyncClient
from storymaster.sync_client.config import SyncClientConfig


def _build_engine(path):
    engine = create_engine(
        f"sqlite:///{path}", connect_args={"check_same_thread": False}
    )
    BaseTable.metadata.create_all(engine)
    return engine


@pytest.fixture
def server_engine(tmp_path):
    return _build_engine(tmp_path / "server.db")


@pytest.fixture
def server_session_factory(server_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=server_engine)


@pytest.fixture
def client_engine(tmp_path):
    return _build_engine(tmp_path / "client.db")


@pytest.fixture
def server_app(server_session_factory):
    """Create the FastAPI app with get_db overridden to use server_engine."""
    from storymaster.sync_server.database import get_db
    from storymaster.sync_server.main import app

    def override_get_db():
        db = server_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def running_server(server_app):
    """Spin uvicorn on a free port, yield base URL, shut down after."""
    import socket

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    config = uvicorn.Config(
        server_app, host="127.0.0.1", port=port, log_level="warning"
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for startup
    deadline = time.time() + 5
    while time.time() < deadline and not server.started:
        time.sleep(0.05)
    if not server.started:
        raise RuntimeError("Server didn't start in time")

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture
def paired_device(server_session_factory):
    """Pre-register a device so we don't need to exercise pairing here."""
    db = server_session_factory()
    try:
        device = SyncDevice(
            device_id="desktop-A", device_name="Desktop A", auth_token="test-token"
        )
        db.add(device)
        db.commit()
        return device.auth_token
    finally:
        db.close()


@pytest.fixture
def server_seed(server_session_factory):
    """Pre-populate the server DB with a User → Setting → Actor."""
    db = server_session_factory()
    try:
        user = User(username="alice")
        db.add(user)
        db.commit()
        setting = Setting(name="World", description="x", user_id=user.id)
        db.add(setting)
        db.commit()
        actor = Actor(first_name="Server-Side", setting_id=setting.id)
        db.add(actor)
        db.commit()
        return {
            "user_uuid": user.sync_uuid,
            "setting_uuid": setting.sync_uuid,
            "actor_uuid": actor.sync_uuid,
        }
    finally:
        db.close()


@pytest.fixture
def client(running_server, paired_device, client_engine):
    config = SyncClientConfig(
        server_url=running_server,
        auth_token=paired_device,
        device_id="desktop-A",
        device_name="Desktop A",
    )
    # Pass a no-op persist so tests never write the user's real
    # ~/.config/storymaster/sync.json.
    return SyncClient(
        config=config, engine=client_engine, persist=lambda _cfg: None
    )


def _client_session(client_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=client_engine)()


def test_pull_replicates_server_rows(client, client_engine, server_seed):
    """A fresh client should pull the server's rows on first sync."""
    summary = client.pull()
    assert summary["accepted"] >= 3  # user, setting, actor at minimum
    assert summary["rejected"] == 0

    db = _client_session(client_engine)
    try:
        actor = db.execute(
            select(Actor).where(Actor.sync_uuid == server_seed["actor_uuid"])
        ).scalar_one()
        setting = db.execute(
            select(Setting).where(Setting.sync_uuid == server_seed["setting_uuid"])
        ).scalar_one()
        # FK was translated to local id, not the server's id.
        assert actor.setting_id == setting.id
        assert actor.first_name == "Server-Side"
    finally:
        db.close()


def test_push_propagates_local_creates(
    client, client_engine, server_session_factory, server_seed
):
    """Local creates should land on the server with FK translation."""
    # Pull first so the client has the parent rows it needs to FK against.
    client.pull()

    db = _client_session(client_engine)
    try:
        local_setting = db.execute(
            select(Setting).where(Setting.sync_uuid == server_seed["setting_uuid"])
        ).scalar_one()
        new_actor = Actor(first_name="Client-Made", setting_id=local_setting.id)
        db.add(new_actor)
        db.commit()
        new_actor_uuid = new_actor.sync_uuid
    finally:
        db.close()

    summary = client.push()
    assert summary["sent"] >= 1
    assert summary["rejected"] == 0
    assert summary["conflicts"] == 0

    server_db = server_session_factory()
    try:
        on_server = server_db.execute(
            select(Actor).where(Actor.sync_uuid == new_actor_uuid)
        ).scalar_one()
        assert on_server.first_name == "Client-Made"
        # On the server side, FK should resolve to the server's setting.id.
        server_setting = server_db.execute(
            select(Setting).where(Setting.sync_uuid == server_seed["setting_uuid"])
        ).scalar_one()
        assert on_server.setting_id == server_setting.id
    finally:
        server_db.close()


def test_push_then_pull_does_not_storm_conflicts(
    client, client_engine, server_session_factory, server_seed
):
    """Regression: after a successful push, the immediately-following pull
    must not re-fetch our own pushed rows as version-mismatch conflicts."""
    # Pull seed rows so the client has them locally.
    client.pull()

    # Make a local edit and push.
    db = _client_session(client_engine)
    try:
        actor = db.execute(
            select(Actor).where(Actor.sync_uuid == server_seed["actor_uuid"])
        ).scalar_one()
        actor.first_name = "Edited"
        db.commit()
    finally:
        db.close()

    push_summary = client.push()
    assert push_summary["accepted"] >= 1
    assert push_summary["conflicts"] == 0

    # The immediate post-push pull should NOT generate conflicts, because the
    # client's local row should already mirror server's bumped version.
    pull_summary = client.pull()
    assert pull_summary["conflicts"] == 0


def test_pull_does_not_bump_version(client, client_engine, server_seed):
    """Client-side apply must mirror server's version, not bump it."""
    client.pull()
    db = _client_session(client_engine)
    try:
        actor = db.execute(
            select(Actor).where(Actor.sync_uuid == server_seed["actor_uuid"])
        ).scalar_one()
        # Server-seeded actor was inserted at version=1.
        assert actor.version == 1
    finally:
        db.close()
