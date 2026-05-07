"""Core sync engine for conflict detection and resolution"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, func, inspect, select, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

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

from storymaster.model.database.schema.base import User

# Map entity type names to SQLAlchemy model classes.
# Order matters for full-sync replays: parents come before children so that
# FK targets exist on the receiver by the time their dependents arrive.
ENTITY_TYPE_MAP = {
    "user": User,
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


# Reverse: SQL table name → model class. Used to resolve FK targets, since
# FK objects in SQLAlchemy reference columns by table name.
TABLE_TO_MODEL = {
    model.__tablename__: model
    for model in ENTITY_TYPE_MAP.values()
    if model is not None
}


# Columns that should never be copied verbatim from incoming data.
# `id` is the sender's *local* primary key — meaningless on the receiver.
# Sync metadata is handled explicitly.
_FIELDS_NOT_DIRECTLY_COPIED = {"id"}


class SyncEngine:
    """Handles synchronization logic and conflict resolution"""

    def __init__(self, db: Session):
        self.db = db
        # Cache of model_class → {column_name: target_table_name} for FK columns.
        self._fk_cache: dict[type, dict[str, str]] = {}

    def _fk_columns(self, model_class) -> dict[str, str]:
        """Return {column_name: target_table_name} for every FK on this model."""
        cached = self._fk_cache.get(model_class)
        if cached is not None:
            return cached
        result: dict[str, str] = {}
        for column in model_class.__table__.columns:
            for fk in column.foreign_keys:
                # fk.column.table.name is the target table.
                result[column.name] = fk.column.table.name
                break  # one target per column
        self._fk_cache[model_class] = result
        return result

    def _lookup_local_id_by_sync_uuid(
        self, table_name: str, sync_uuid: str
    ) -> Optional[int]:
        """Find the local integer id of a row in `table_name` with the given sync_uuid."""
        model = TABLE_TO_MODEL.get(table_name)
        if model is None or sync_uuid is None:
            return None
        stmt = select(model.id).where(model.sync_uuid == sync_uuid)
        return self.db.execute(stmt).scalar_one_or_none()

    def _lookup_sync_uuid_by_local_id(
        self, table_name: str, local_id: Optional[int]
    ) -> Optional[str]:
        """Find the sync_uuid of a row in `table_name` by its local integer id."""
        if local_id is None:
            return None
        model = TABLE_TO_MODEL.get(table_name)
        if model is None:
            return None
        stmt = select(model.sync_uuid).where(model.id == local_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def _augment_with_fk_uuids(self, model_class, data: dict) -> dict:
        """For each FK column, add a sibling `<col>_sync_uuid` resolving the target row."""
        fks = self._fk_columns(model_class)
        for col_name, target_table in fks.items():
            local_id = data.get(col_name)
            data[f"{col_name}_sync_uuid"] = self._lookup_sync_uuid_by_local_id(
                target_table, local_id
            )
        return data

    def _resolve_fk_uuids_to_local_ids(
        self, model_class, data: dict
    ) -> tuple[dict, list[str]]:
        """
        Replace `<col>_sync_uuid` keys in `data` with `<col>` containing the
        receiver's local id for that target row. Returns (translated_data, missing_targets).
        `missing_targets` lists target tables we couldn't resolve — caller should
        reject the change so the sender retries after dependencies arrive.
        """
        translated = dict(data)
        fks = self._fk_columns(model_class)
        missing: list[str] = []
        for col_name, target_table in fks.items():
            uuid_key = f"{col_name}_sync_uuid"
            if uuid_key not in translated:
                continue
            target_uuid = translated.pop(uuid_key)
            if target_uuid is None:
                # FK is null — preserve as null
                translated[col_name] = None
                continue
            local_id = self._lookup_local_id_by_sync_uuid(target_table, target_uuid)
            if local_id is None:
                missing.append(f"{target_table}:{target_uuid}")
                continue
            translated[col_name] = local_id
        return translated, missing

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
                    # Translate FK target ids → sync_uuids so the receiver can map
                    # them to its own local ids.
                    data = self._augment_with_fk_uuids(model_class, data)

                # Create EntityChange with explicit conversion of all fields
                change = EntityChange(
                    entity_type=entity_type,
                    entity_id=int(entity.id),
                    sync_uuid=entity.sync_uuid,
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
        self,
        device: Optional[SyncDevice],
        changes: list[EntityChange],
        bump_versions: bool = True,
    ) -> dict[str, Any]:
        """
        Apply incoming changes against the local DB. Identifies rows by sync_uuid,
        not the sender's local id. Translates FK references via `<col>_sync_uuid`.

        bump_versions=True (server-side push handler): increment row version on
        update and stamp updated_at to now. The server is the canonical writer
        that issues the new version other peers will see on their next pull.

        bump_versions=False (client-side pull handler): mirror the incoming
        version and updated_at as-is. The server already bumped them; the local
        DB is just a replica.

        device may be None on the client side (no SyncLog row written).

        Returns dict with accepted, conflicts, and rejected counts.
        """
        accepted = 0
        rejected = 0
        conflicts: list[ConflictInfo] = []

        for change in changes:
            model_class = ENTITY_TYPE_MAP.get(change.entity_type)
            if model_class is None:
                rejected += 1
                continue

            try:
                if change.operation == "delete":
                    result = self._apply_delete(device, model_class, change, bump_versions)
                elif change.operation in ("create", "update"):
                    result = self._apply_upsert(device, model_class, change, bump_versions)
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
                logger.exception(
                    "Error applying %s change for %s sync_uuid=%s: %s",
                    change.operation, change.entity_type, change.sync_uuid, e,
                )
                rejected += 1

        return {"accepted": accepted, "conflicts": conflicts, "rejected": rejected}

    def _find_by_sync_uuid(self, model_class, sync_uuid: str):
        """Look up a single row by sync_uuid, or None."""
        if not sync_uuid:
            return None
        stmt = select(model_class).where(model_class.sync_uuid == sync_uuid)
        return self.db.execute(stmt).scalar_one_or_none()

    def _apply_upsert(
        self,
        device: Optional[SyncDevice],
        model_class,
        change: EntityChange,
        bump_versions: bool,
    ) -> dict[str, Any]:
        """
        Insert if no row with this sync_uuid exists; otherwise update with
        optimistic version check.
        """
        if change.sync_uuid is None or change.data is None:
            return {"status": "rejected"}

        # Translate FK sync_uuids → local ids before touching the row.
        translated, missing = self._resolve_fk_uuids_to_local_ids(
            model_class, change.data
        )
        if missing:
            logger.warning(
                "Rejecting %s change for %s sync_uuid=%s: missing FK targets %s",
                change.operation, change.entity_type, change.sync_uuid, missing,
            )
            return {"status": "rejected"}

        existing = self._find_by_sync_uuid(model_class, change.sync_uuid)

        if existing is None:
            return self._insert_new(device, model_class, change, translated)

        return self._update_existing(
            device, model_class, change, translated, existing, bump_versions
        )

    def _insert_new(
        self,
        device: Optional[SyncDevice],
        model_class,
        change: EntityChange,
        translated_data: dict,
    ) -> dict[str, Any]:
        """Create a new row from a peer's change."""
        # Strip the sender's local id; let our autoincrement assign one.
        clean = {
            key: self._convert_value_for_column(model_class, key, value)
            for key, value in translated_data.items()
            if key not in _FIELDS_NOT_DIRECTLY_COPIED
        }
        # Ensure sync_uuid lands on the new row.
        clean["sync_uuid"] = change.sync_uuid

        new_entity = model_class(**clean)
        self.db.add(new_entity)
        self.db.commit()

        self._log_sync(device, change.entity_type, new_entity.id, "create")
        return {"status": "accepted"}

    def _update_existing(
        self,
        device: Optional[SyncDevice],
        model_class,
        change: EntityChange,
        translated_data: dict,
        existing,
        bump_versions: bool,
    ) -> dict[str, Any]:
        """Update an existing row with optimistic version checking."""
        if change.version is None:
            return {"status": "rejected"}

        if existing.version != change.version:
            return {
                "status": "conflict",
                "conflict": ConflictInfo(
                    entity_type=change.entity_type,
                    entity_id=existing.id,
                    sync_uuid=existing.sync_uuid,
                    mobile_version=change.version,
                    desktop_version=existing.version,
                    mobile_updated_at=change.updated_at or datetime.now(timezone.utc),
                    desktop_updated_at=self._ensure_timezone_aware(existing.updated_at)
                    or datetime.now(timezone.utc),
                    mobile_data=change.data,
                    desktop_data=existing.as_dict(),
                    resolution="merge",
                ),
            }

        for key, value in translated_data.items():
            if key in _FIELDS_NOT_DIRECTLY_COPIED:
                continue
            if key == "sync_uuid":
                continue  # never overwrite the row's own identity
            if hasattr(existing, key):
                converted = self._convert_value_for_column(model_class, key, value)
                setattr(existing, key, converted)

        if bump_versions:
            existing.version += 1
            existing.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        self._log_sync(device, change.entity_type, existing.id, "update")
        return {"status": "accepted"}

    def _apply_delete(
        self,
        device: Optional[SyncDevice],
        model_class,
        change: EntityChange,
        bump_versions: bool,
    ) -> dict[str, Any]:
        """Soft-delete by sync_uuid. Idempotent if row is missing."""
        if change.sync_uuid is None:
            return {"status": "rejected"}

        existing = self._find_by_sync_uuid(model_class, change.sync_uuid)
        if existing is None:
            return {"status": "accepted"}

        existing.deleted_at = datetime.now(timezone.utc)
        if bump_versions:
            existing.version += 1
        self.db.commit()

        self._log_sync(device, change.entity_type, existing.id, "delete")
        return {"status": "accepted"}

    def _log_sync(
        self,
        device: Optional[SyncDevice],
        entity_type: str,
        entity_id: int,
        operation: str,
    ):
        """Log sync operation for tracking. Skipped when no device (client-side pulls)."""
        if device is None:
            return
        log_entry = SyncLog(
            device_id=device.id,
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
        )
        self.db.add(log_entry)
        self.db.commit()
