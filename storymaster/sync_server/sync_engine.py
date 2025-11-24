"""Core sync engine for conflict detection and resolution"""

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, func, inspect, select, text
from sqlalchemy.orm import Session

from storymaster.model.database.schema.base import (
    Actor,
    ActorAOnBRelations,
    ActorToClass,
    ActorToRace,
    ActorToSkills,
    ActorToStat,
    ArcPoint,
    ArcToActor,
    ArcToNode,
    ArcType,
    Background,
    Class_,
    Faction,
    FactionAOnBRelations,
    FactionMembers,
    History,
    HistoryActor,
    HistoryFaction,
    HistoryLocation,
    HistoryObject,
    HistoryWorldData,
    LitographyArc,
    LitographyNode,
    LitographyNodeToPlotSection,
    LitographyNotes,
    LitographyPlot,
    LitographyPlotSection,
    Location,
    LocationCity,
    LocationCityDistricts,
    LocationDungeon,
    LocationFloraFauna,
    NodeConnection,
    Object_,
    ObjectToOwner,
    Race,
    Resident,
    Setting,
    Skills,
    Stat,
    Storyline,
    StorylineToSetting,
    SubRace,
    SyncDevice,
    SyncLog,
    WorldData,
)
from storymaster.sync_server.models import ConflictInfo, EntityChange

# Map entity type names to SQLAlchemy model classes
ENTITY_TYPE_MAP = {
    "user": None,  # Skip user sync for now
    "storyline": Storyline,
    "setting": Setting,
    "storyline_to_setting": StorylineToSetting,
    "actor": Actor,
    "actor_a_on_b_relations": ActorAOnBRelations,
    "actor_to_class": ActorToClass,
    "actor_to_race": ActorToRace,
    "actor_to_skills": ActorToSkills,
    "actor_to_stat": ActorToStat,
    "faction": Faction,
    "faction_a_on_b_relations": FactionAOnBRelations,
    "faction_members": FactionMembers,
    "location": Location,
    "location_city": LocationCity,
    "location_city_districts": LocationCityDistricts,
    "location_dungeon": LocationDungeon,
    "location_flora_fauna": LocationFloraFauna,
    "residents": Resident,
    "object_": Object_,
    "object_to_owner": ObjectToOwner,
    "world_data": WorldData,
    "history": History,
    "history_actor": HistoryActor,
    "history_faction": HistoryFaction,
    "history_location": HistoryLocation,
    "history_object": HistoryObject,
    "history_world_data": HistoryWorldData,
    "litography_plot": LitographyPlot,
    "litography_plot_section": LitographyPlotSection,
    "litography_node": LitographyNode,
    "litography_node_to_plot_section": LitographyNodeToPlotSection,
    "node_connection": NodeConnection,
    "litography_notes": LitographyNotes,
    "litography_arc": LitographyArc,
    "arc_point": ArcPoint,
    "arc_type": ArcType,
    "arc_to_node": ArcToNode,
    "arc_to_actor": ArcToActor,
    "class": Class_,
    "background": Background,
    "race": Race,
    "sub_race": SubRace,
    "skills": Skills,
    "stat": Stat,
}


class SyncEngine:
    """Handles synchronization logic and conflict resolution"""

    def __init__(self, db: Session):
        self.db = db

    def _ensure_timezone_aware(self, dt: Optional[datetime]) -> Optional[datetime]:
        """Ensure datetime is timezone-aware (UTC if naive)"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _convert_value_for_column(self, model_class, column_name: str, value: Any) -> Any:
        """Convert a value to the appropriate type for a SQLAlchemy column"""
        if value is None:
            return None

        # Get the column type from the model
        try:
            column = model_class.__table__.columns[column_name]
            column_type = column.type

            # Handle datetime columns - parse string to datetime
            if isinstance(column_type, DateTime):
                if isinstance(value, str):
                    # Parse ISO format datetime string
                    # Handle 'Z' suffix (Zulu time = UTC)
                    if value.endswith('Z'):
                        value = value[:-1] + '+00:00'
                    parsed = datetime.fromisoformat(value)
                    # Ensure timezone-aware
                    return self._ensure_timezone_aware(parsed)
                elif isinstance(value, datetime):
                    return self._ensure_timezone_aware(value)

            # For all other types, return as-is
            return value

        except (KeyError, AttributeError):
            # Column doesn't exist or can't get type, return value as-is
            return value

    def get_changes_since(
        self,
        since_timestamp: Optional[datetime] = None,
        entity_types: Optional[list[str]] = None,
    ) -> list[EntityChange]:
        """
        Get all entity changes since the given timestamp.
        If since_timestamp is None, returns all entities (full sync).
        """
        changes = []

        # Ensure since_timestamp is timezone-aware for comparisons
        since_timestamp = self._ensure_timezone_aware(since_timestamp)

        # Determine which entity types to sync
        types_to_sync = entity_types if entity_types else ENTITY_TYPE_MAP.keys()

        for entity_type in types_to_sync:
            model_class = ENTITY_TYPE_MAP.get(entity_type)
            if model_class is None:
                continue  # Skip unsupported types

            # Build query
            stmt = select(model_class)

            # Filter by timestamp if provided (incremental sync)
            if since_timestamp:
                stmt = stmt.where(model_class.updated_at > since_timestamp)

            # Execute query
            entities = self.db.execute(stmt).scalars().all()

            # Convert to EntityChange objects
            for entity in entities:
                # Ensure entity datetimes are timezone-aware (SQLite returns naive datetimes)
                entity_created_at = self._ensure_timezone_aware(entity.created_at)
                entity_updated_at = self._ensure_timezone_aware(entity.updated_at)

                # Determine operation type
                if entity.deleted_at is not None:
                    operation = "delete"
                    data = None
                else:
                    # Check if created after since_timestamp
                    if since_timestamp and entity_created_at > since_timestamp:
                        operation = "create"
                    else:
                        operation = "update"
                    # Get dict representation (already JSON-serializable from as_dict())
                    data = entity.as_dict()

                # Create EntityChange with explicit conversion of all fields
                change = EntityChange(
                    entity_type=entity_type,
                    entity_id=int(entity.id),
                    operation=operation,
                    entity_data=data,
                    version=int(entity.version),
                    updated_at=entity_updated_at,
                )
                changes.append(change)

        return changes

    def count_changes_since(self, since_timestamp: Optional[datetime] = None) -> int:
        """Count total changes since timestamp"""
        # Ensure since_timestamp is timezone-aware for comparisons
        since_timestamp = self._ensure_timezone_aware(since_timestamp)

        total = 0
        for model_class in ENTITY_TYPE_MAP.values():
            if model_class is None:
                continue

            # Use SQL COUNT for efficiency
            stmt = select(func.count()).select_from(model_class)

            # Filter by timestamp if provided (incremental sync)
            if since_timestamp is not None:
                stmt = stmt.where(model_class.updated_at > since_timestamp)

            count = self.db.execute(stmt).scalar() or 0
            total += count

        return total

    def apply_changes(
        self, device: SyncDevice, changes: list[EntityChange]
    ) -> dict[str, Any]:
        """
        Apply changes from mobile device with conflict detection.
        Returns dict with accepted, conflicts, and rejected counts.
        """
        accepted = 0
        rejected = 0
        conflicts = []

        for change in changes:
            model_class = ENTITY_TYPE_MAP.get(change.entity_type)
            if model_class is None:
                rejected += 1
                continue

            try:
                if change.operation == "delete":
                    result = self._apply_delete(device, model_class, change)
                elif change.operation == "create":
                    result = self._apply_create(device, model_class, change)
                elif change.operation == "update":
                    result = self._apply_update(device, model_class, change)
                else:
                    rejected += 1
                    continue

                if result["status"] == "accepted":
                    accepted += 1
                elif result["status"] == "conflict":
                    conflicts.append(result["conflict"])
                else:
                    rejected += 1

            except Exception as e:
                print(f"Error applying change: {e}")
                rejected += 1

        return {"accepted": accepted, "conflicts": conflicts, "rejected": rejected}

    def _apply_create(
        self, device: SyncDevice, model_class, change: EntityChange
    ) -> dict[str, Any]:
        """Apply a create operation"""
        # Validate required fields for conflict detection
        if change.version is None or change.updated_at is None:
            return {"status": "rejected"}

        # Check if entity already exists
        existing = self.db.get(model_class, change.entity_id)
        if existing:
            # Entity exists - this is a conflict
            return {
                "status": "conflict",
                "conflict": ConflictInfo(
                    entity_type=change.entity_type,
                    entity_id=change.entity_id,
                    mobile_version=change.version,
                    desktop_version=existing.version,
                    mobile_updated_at=change.updated_at,
                    desktop_updated_at=existing.updated_at,
                    mobile_data=change.data,
                    desktop_data=existing.as_dict(),
                    resolution="desktop_wins",  # Default: desktop wins on create conflicts
                ),
            }

        # Create new entity - convert values to appropriate types
        if change.data is None:
            return {"status": "rejected"}

        converted_data = {}
        for key, value in change.data.items():
            converted_data[key] = self._convert_value_for_column(model_class, key, value)

        new_entity = model_class(**converted_data)
        self.db.add(new_entity)
        self.db.commit()

        # Log sync operation
        self._log_sync(device, change.entity_type, change.entity_id, "create")

        return {"status": "accepted"}

    def _apply_update(
        self, device: SyncDevice, model_class, change: EntityChange
    ) -> dict[str, Any]:
        """Apply an update operation with conflict detection"""
        # Validate required fields for conflict detection
        if change.version is None or change.updated_at is None:
            return {"status": "rejected"}

        # Get existing entity
        existing = self.db.get(model_class, change.entity_id)
        if not existing:
            # Entity doesn't exist - reject
            return {"status": "rejected"}

        # Check for version conflict
        if existing.version != change.version:
            # Version mismatch - conflict detected
            return {
                "status": "conflict",
                "conflict": ConflictInfo(
                    entity_type=change.entity_type,
                    entity_id=change.entity_id,
                    mobile_version=change.version,
                    desktop_version=existing.version,
                    mobile_updated_at=change.updated_at,
                    desktop_updated_at=existing.updated_at,
                    mobile_data=change.data,
                    desktop_data=existing.as_dict(),
                    resolution="merge",  # Attempt to merge
                ),
            }

        # No conflict - apply update
        if change.data is None:
            print(f"⚠️  Rejecting update: change.data is None")
            return {"status": "rejected"}

        print(f"✅ Applying update to {change.entity_type} #{change.entity_id}")
        print(f"   Incoming data keys: {list(change.data.keys())}")
        print(f"   Incoming version: {change.version}, Existing version: {existing.version}")

        for key, value in change.data.items():
            if hasattr(existing, key):
                # Convert value to appropriate type for the column
                converted_value = self._convert_value_for_column(model_class, key, value)
                old_value = getattr(existing, key)
                setattr(existing, key, converted_value)
                if old_value != converted_value:
                    print(f"   Updated {key}: {repr(old_value)} → {repr(converted_value)}")

        # Increment version
        existing.version += 1
        existing.updated_at = datetime.now(timezone.utc)

        print(f"   New version: {existing.version}")
        print(f"   Committing changes...")
        self.db.commit()
        print(f"   ✓ Committed!")

        # Log sync operation
        self._log_sync(device, change.entity_type, change.entity_id, "update")

        return {"status": "accepted"}

    def _apply_delete(
        self, device: SyncDevice, model_class, change: EntityChange
    ) -> dict[str, Any]:
        """Apply a delete operation (soft delete)"""
        existing = self.db.get(model_class, change.entity_id)
        if not existing:
            # Entity doesn't exist - accept (idempotent)
            return {"status": "accepted"}

        # Soft delete
        existing.deleted_at = datetime.now(timezone.utc)
        existing.version += 1
        self.db.commit()

        # Log sync operation
        self._log_sync(device, change.entity_type, change.entity_id, "delete")

        return {"status": "accepted"}

    def _log_sync(
        self, device: SyncDevice, entity_type: str, entity_id: int, operation: str
    ):
        """Log sync operation for tracking"""
        log_entry = SyncLog(
            device_id=device.id,
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
        )
        self.db.add(log_entry)
        self.db.commit()
