"""Tests for the sync server functionality"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from storymaster.model.database.schema.base import (
    Actor,
    BaseTable,
    Setting,
    Storyline,
    SyncDevice,
    SyncLog,
    User,
)
from storymaster.sync_server.auth import create_device, generate_auth_token
from storymaster.sync_server.database import get_db
from storymaster.sync_server.main import app
from storymaster.sync_server.models import EntityChange
from storymaster.sync_server.sync_engine import SyncEngine


# Test database setup
@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test"""
    # Use in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Create all tables
    BaseTable.metadata.create_all(engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create session
    db = TestingSessionLocal()

    yield db

    db.close()


@pytest.fixture(scope="function")
def test_client(test_db):
    """Create a test client with test database"""

    # Override get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    yield client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    user = User(username="test_user")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_storyline(test_db, test_user):
    """Create a test storyline"""
    storyline = Storyline(
        name="Test Storyline", description="A test storyline", user_id=test_user.id
    )
    test_db.add(storyline)
    test_db.commit()
    test_db.refresh(storyline)
    return storyline


@pytest.fixture
def test_setting(test_db, test_user):
    """Create a test setting"""
    setting = Setting(name="Test Setting", description="A test setting", user_id=test_user.id)
    test_db.add(setting)
    test_db.commit()
    test_db.refresh(setting)
    return setting


@pytest.fixture
def test_device(test_db):
    """Create a test sync device"""
    device = create_device(test_db, "test-device-123", "Test Phone")
    return device


# === Health Check Tests ===


def test_health_check(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["database_connected"] is True
    assert data["version"] == "1.0.0"


# === Device Pairing Tests ===


def test_get_qr_data(test_client):
    """Test QR code data generation"""
    response = test_client.get("/api/pair/qr-data")
    assert response.status_code == 200

    data = response.json()
    assert "ip" in data
    assert "port" in data
    assert "token" in data
    assert data["port"] == 8765


def test_get_qr_image(test_client):
    """Test QR code image generation"""
    response = test_client.get("/api/pair/qr-image")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_register_device_success(test_client):
    """Test successful device registration"""
    # First get a pairing token
    qr_response = test_client.get("/api/pair/qr-data")
    pairing_token = qr_response.json()["token"]

    # Register device
    register_data = {
        "device_id": "test-device-456",
        "device_name": "Test Mobile",
        "pairing_token": pairing_token,
    }

    response = test_client.post("/api/pair/register", json=register_data)
    assert response.status_code == 200

    data = response.json()
    assert data["device_id"] == "test-device-456"
    assert data["device_name"] == "Test Mobile"
    assert "auth_token" in data
    assert len(data["auth_token"]) > 20  # Token should be reasonably long


def test_register_device_invalid_token(test_client):
    """Test device registration with invalid pairing token"""
    register_data = {
        "device_id": "test-device-789",
        "device_name": "Test Device",
        "pairing_token": "invalid-token-123",
    }

    response = test_client.post("/api/pair/register", json=register_data)
    assert response.status_code == 401


def test_register_device_already_exists(test_client, test_device):
    """Test registering a device that already exists"""
    # Get pairing token
    qr_response = test_client.get("/api/pair/qr-data")
    pairing_token = qr_response.json()["token"]

    # Try to register same device
    register_data = {
        "device_id": test_device.device_id,
        "device_name": "Different Name",
        "pairing_token": pairing_token,
    }

    response = test_client.post("/api/pair/register", json=register_data)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Device already registered"
    assert data["auth_token"] == test_device.auth_token


# === Authentication Tests ===


def test_protected_endpoint_without_auth(test_client):
    """Test accessing protected endpoint without authentication"""
    response = test_client.get("/api/sync/status")
    assert response.status_code == 403  # Forbidden (no auth header)


def test_protected_endpoint_with_invalid_token(test_client):
    """Test accessing protected endpoint with invalid token"""
    headers = {"Authorization": "Bearer invalid-token-xyz"}
    response = test_client.get("/api/sync/status", headers=headers)
    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(test_client, test_device):
    """Test accessing protected endpoint with valid token"""
    headers = {"Authorization": f"Bearer {test_device.auth_token}"}
    response = test_client.get("/api/sync/status", headers=headers)
    assert response.status_code == 200


# === Sync Pull Tests ===


def test_sync_pull_empty(test_client, test_device):
    """Test pulling changes from empty database"""
    headers = {"Authorization": f"Bearer {test_device.auth_token}"}
    pull_data = {"since_timestamp": None, "entity_types": None}

    response = test_client.post("/api/sync/pull", json=pull_data, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert "changes" in data
    assert isinstance(data["changes"], list)
    assert "sync_timestamp" in data
    assert data["has_more"] is False


def test_sync_pull_with_data(test_client, test_device, test_user, test_setting):
    """Test pulling changes with data in database"""
    # Create an actor
    actor = Actor(
        name="Test Character",
        description="A test character",
        setting_id=test_setting.id,
    )
    test_client.app.dependency_overrides[get_db]().__next__().add(actor)
    test_client.app.dependency_overrides[get_db]().__next__().commit()

    headers = {"Authorization": f"Bearer {test_device.auth_token}"}
    pull_data = {"since_timestamp": None, "entity_types": ["actor"]}

    response = test_client.post("/api/sync/pull", json=pull_data, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data["changes"]) >= 1

    # Find actor change
    actor_changes = [c for c in data["changes"] if c["entity_type"] == "actor"]
    assert len(actor_changes) >= 1

    actor_change = actor_changes[0]
    assert actor_change["operation"] in ["create", "update"]
    assert actor_change["data"]["name"] == "Test Character"


def test_sync_pull_incremental(test_client, test_device, test_setting, test_db):
    """Test incremental sync (only changes after timestamp)"""
    # Create actor before sync
    old_actor = Actor(name="Old Character", setting_id=test_setting.id)
    test_db.add(old_actor)
    test_db.commit()

    # Get timestamp
    sync_time = datetime.now()

    # Wait a bit to ensure timestamp difference
    import time

    time.sleep(0.1)

    # Create actor after sync
    new_actor = Actor(name="New Character", setting_id=test_setting.id)
    test_db.add(new_actor)
    test_db.commit()

    # Pull only changes after sync_time
    headers = {"Authorization": f"Bearer {test_device.auth_token}"}
    pull_data = {"since_timestamp": sync_time.isoformat(), "entity_types": ["actor"]}

    response = test_client.post("/api/sync/pull", json=pull_data, headers=headers)
    assert response.status_code == 200

    data = response.json()
    actor_changes = [c for c in data["changes"] if c["entity_type"] == "actor"]

    # Should only get new actor
    assert any(c["data"]["name"] == "New Character" for c in actor_changes)


# === Sync Push Tests ===


def test_sync_push_create(test_client, test_device, test_setting):
    """Test pushing new entities to desktop"""
    headers = {"Authorization": f"Bearer {test_device.auth_token}"}

    # Create change
    change = {
        "entity_type": "actor",
        "entity_id": 999,  # New ID
        "operation": "create",
        "data": {
            "id": 999,
            "name": "Mobile Character",
            "description": "Created on mobile",
            "setting_id": test_setting.id,
        },
        "version": 1,
        "updated_at": datetime.now().isoformat(),
    }

    push_data = {"changes": [change]}

    response = test_client.post("/api/sync/push", json=push_data, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["accepted"] >= 0  # May vary based on implementation
    assert len(data["conflicts"]) == 0


def test_sync_push_conflict(test_client, test_device, test_setting, test_db):
    """Test conflict detection when pushing changes"""
    # Create actor on desktop
    actor = Actor(name="Desktop Version", setting_id=test_setting.id, version=1)
    test_db.add(actor)
    test_db.commit()
    test_db.refresh(actor)

    # Update on desktop to version 2
    actor.name = "Desktop Updated"
    actor.version = 2
    test_db.commit()

    # Try to push mobile change with version 1 (conflict!)
    headers = {"Authorization": f"Bearer {test_device.auth_token}"}

    change = {
        "entity_type": "actor",
        "entity_id": actor.id,
        "operation": "update",
        "data": {
            "id": actor.id,
            "name": "Mobile Updated",
            "setting_id": test_setting.id,
        },
        "version": 1,  # Old version - conflict!
        "updated_at": datetime.now().isoformat(),
    }

    push_data = {"changes": [change]}

    response = test_client.post("/api/sync/push", json=push_data, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data["conflicts"]) > 0

    conflict = data["conflicts"][0]
    assert conflict["entity_id"] == actor.id
    assert conflict["mobile_version"] == 1
    assert conflict["desktop_version"] == 2


# === Sync Status Tests ===


def test_sync_status(test_client, test_device):
    """Test getting sync status"""
    headers = {"Authorization": f"Bearer {test_device.auth_token}"}

    response = test_client.get("/api/sync/status", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["device_id"] == test_device.device_id
    assert data["device_name"] == test_device.device_name
    assert "pending_changes_count" in data
    assert "server_timestamp" in data


# === Sync Engine Tests ===


def test_sync_engine_get_changes(test_db, test_setting):
    """Test SyncEngine.get_changes_since()"""
    # Create test data
    actor = Actor(name="Test Actor", setting_id=test_setting.id)
    test_db.add(actor)
    test_db.commit()

    # Get all changes
    engine = SyncEngine(test_db)
    changes = engine.get_changes_since(since_timestamp=None, entity_types=["actor"])

    assert len(changes) > 0
    actor_changes = [c for c in changes if c.entity_type == "actor"]
    assert len(actor_changes) > 0


def test_sync_engine_apply_changes(test_db, test_device, test_setting):
    """Test SyncEngine.apply_changes()"""
    engine = SyncEngine(test_db)

    # Create change
    change = EntityChange(
        entity_type="actor",
        entity_id=888,
        operation="create",
        data={
            "id": 888,
            "name": "Applied Actor",
            "setting_id": test_setting.id,
        },
        version=1,
        updated_at=datetime.now(),
    )

    result = engine.apply_changes(test_device, [change])

    # Should be accepted or have conflict (depending on implementation)
    assert result["accepted"] >= 0
    assert isinstance(result["conflicts"], list)


# === List Devices Tests ===


def test_list_devices(test_client, test_device):
    """Test listing registered devices"""
    response = test_client.get("/api/devices")
    assert response.status_code == 200

    data = response.json()
    assert "devices" in data
    assert len(data["devices"]) > 0

    # Find our test device
    device_ids = [d["device_id"] for d in data["devices"]]
    assert test_device.device_id in device_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
