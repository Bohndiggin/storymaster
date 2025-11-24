"""Pydantic models for API request/response validation"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator


# === Pairing / QR Code Models ===


class QRCodeResponse(BaseModel):
    """Response containing QR code data for device pairing"""

    ip: str = Field(..., description="Server IP address")
    port: int = Field(..., description="Server port")
    token: str = Field(..., description="Authentication token for pairing")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")


class DevicePairRequest(BaseModel):
    """Request to pair a new device"""

    device_id: str = Field(..., description="Unique device identifier (UUID)")
    device_name: str = Field(..., description="Human-readable device name")
    pairing_token: str = Field(..., description="Token from QR code")


class DevicePairResponse(BaseModel):
    """Response after successful device pairing"""

    device_id: str
    device_name: str
    auth_token: str = Field(..., description="Permanent auth token for API calls")
    message: str = "Device paired successfully"


# === Sync Models ===


class EntityChange(BaseModel):
    """Represents a change to a single entity"""

    model_config = ConfigDict(
        ser_json_timedelta='iso8601',
        populate_by_name=True  # Allow field aliases
    )

    entity_type: str = Field(..., description="Table name (e.g., 'actor', 'location')")
    entity_id: int = Field(..., description="Primary key of the entity")
    operation: str = Field(..., description="'create', 'update', or 'delete')")
    data: Optional[dict[str, Any]] = Field(
        None,
        alias="entity_data",  # Accept both "data" and "entity_data"
        description="Entity data (null for deletes)"
    )
    version: Optional[int] = Field(None, description="Entity version for conflict detection")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the change")

    @model_validator(mode='before')
    @classmethod
    def extract_version_and_timestamp(cls, values):
        """Extract version and updated_at from entity_data if not at top level"""
        if isinstance(values, dict):
            # Handle both "data" and "entity_data" field names
            entity_data = values.get('data') or values.get('entity_data')

            if entity_data and isinstance(entity_data, dict):
                # Extract version if not at top level
                if 'version' not in values and 'version' in entity_data:
                    values['version'] = entity_data['version']

                # Extract updated_at if not at top level
                if 'updated_at' not in values and 'updated_at' in entity_data:
                    values['updated_at'] = entity_data['updated_at']

                # Also check created_at as fallback for updated_at
                if 'updated_at' not in values and 'created_at' in entity_data:
                    values['updated_at'] = entity_data['created_at']

        return values

    @field_serializer('data')
    def serialize_data(self, value: Optional[dict[str, Any]], _info) -> Optional[dict[str, Any]]:
        """Ensure data dict is JSON-serializable"""
        if value is None:
            return None

        # Recursively ensure all values in the dict are JSON-serializable
        return self._make_serializable(value)

    def _make_serializable(self, obj):
        """Recursively convert objects to JSON-serializable types"""
        if obj is None:
            return None
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            # For any other types (including SQLAlchemy objects), convert to string
            return str(obj)


class SyncPullRequest(BaseModel):
    """Request to pull changes from desktop"""

    since_timestamp: Optional[datetime] = Field(
        None, description="Only get changes after this time (null = full sync)"
    )
    entity_types: Optional[list[str]] = Field(
        None, description="Filter by entity types (null = all types)"
    )


class SyncPullResponse(BaseModel):
    """Response with changes to pull from desktop"""

    changes: list[EntityChange] = Field(..., description="List of entity changes")
    sync_timestamp: datetime = Field(..., description="Server timestamp of this sync")
    has_more: bool = Field(False, description="True if more changes exist (pagination)")


class SyncPushRequest(BaseModel):
    """Request to push changes to desktop"""

    changes: list[EntityChange] = Field(..., description="Changes from mobile device")


class ConflictInfo(BaseModel):
    """Information about a sync conflict"""

    model_config = ConfigDict(ser_json_timedelta='iso8601')

    entity_type: str
    entity_id: int
    mobile_version: int
    desktop_version: int
    mobile_updated_at: datetime
    desktop_updated_at: datetime
    mobile_data: dict[str, Any]
    desktop_data: dict[str, Any]
    resolution: str = Field(..., description="'merge', 'mobile_wins', or 'desktop_wins'")

    @field_serializer('mobile_data', 'desktop_data')
    def serialize_data(self, value: dict[str, Any], _info) -> dict[str, Any]:
        """Ensure data dicts are JSON-serializable"""
        return self._make_serializable(value)

    def _make_serializable(self, obj):
        """Recursively convert objects to JSON-serializable types"""
        if obj is None:
            return None
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            # For any other types (including SQLAlchemy objects), convert to string
            return str(obj)


class SyncPushResponse(BaseModel):
    """Response after pushing changes"""

    accepted: int = Field(..., description="Number of changes accepted")
    conflicts: list[ConflictInfo] = Field([], description="Conflicts that need resolution")
    rejected: int = Field(0, description="Number of changes rejected")
    message: str = "Sync completed"


class SyncStatusResponse(BaseModel):
    """Current sync status"""

    device_id: str
    device_name: str
    last_sync_at: Optional[datetime]
    pending_changes_count: int = Field(..., description="Changes waiting to be pulled")
    server_timestamp: datetime = Field(..., description="Current server time")


# === Health Check Models ===


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = "ok"
    timestamp: datetime
    database_connected: bool = True
    version: str = "1.0.0"
