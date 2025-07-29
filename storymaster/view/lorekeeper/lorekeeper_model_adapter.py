"""Adapter to connect new Lorekeeper interface to existing model"""

from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session

from storymaster.model.common.common_model import BaseModel
from storymaster.model.database.schema.base import (
    Actor,
    Faction,
    Location,
    Object_,
    History,
    WorldData,
    Background,
    Race,
    Class_,
    Skills,
    SubRace,
    Alignment,
    Stat,
    LocationDungeon,
    LocationCity,
    LocationCityDistricts,
    LocationFloraFauna,
    LitographyNotes,
)


class LorekeeperModelAdapter:
    """Adapter class to connect the new Lorekeeper UI to the existing model"""

    def __init__(self, model: BaseModel, setting_id: int):
        self.model = model
        self.setting_id = setting_id

        # Mapping of table names to SQLAlchemy classes
        self.table_classes = {
            "actor": Actor,
            "faction": Faction,
            "location_": Location,
            "object_": Object_,
            "history": History,
            "world_data": WorldData,
            "background": Background,
            "race": Race,
            "class": Class_,
            "skills": Skills,
            "sub_race": SubRace,
            "alignment": Alignment,
            "stat": Stat,
            "litography_notes": LitographyNotes,
        }

    def get_entities(self, table_name: str) -> List[Any]:
        """Get all entities for a given table type"""
        table_class = self.table_classes.get(table_name)
        if not table_class:
            return []

        try:
            with Session(self.model.engine) as session:
                # Notes use storyline_id instead of setting_id
                if table_name == "litography_notes":
                    # For now, get all storylines for this setting and get notes for all of them
                    from storymaster.model.database.schema.base import (
                        Storyline,
                        StorylineToSetting,
                    )
                    from sqlalchemy.orm import joinedload

                    storylines = (
                        session.query(Storyline)
                        .join(StorylineToSetting)
                        .filter(StorylineToSetting.setting_id == self.setting_id)
                        .all()
                    )

                    all_notes = []
                    for storyline in storylines:
                        notes = (
                            session.query(table_class)
                            .options(joinedload(table_class.linked_node))
                            .filter_by(storyline_id=storyline.id)
                            .all()
                        )
                        all_notes.extend(notes)
                    return all_notes
                else:
                    from sqlalchemy.orm import joinedload
                    
                    query = session.query(table_class).filter_by(setting_id=self.setting_id)
                    
                    # Add eager loading for commonly accessed relationships
                    if table_name == "actor":
                        query = query.options(
                            joinedload(table_class.background),
                            joinedload(table_class.alignment),
                            joinedload(table_class.setting)
                        )
                    elif table_name == "faction":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    elif table_name == "location_":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    elif table_name == "object_":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    elif table_name == "history":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    elif table_name == "world_data":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    
                    return query.all()
        except Exception as e:
            print(f"Error loading entities for {table_name}: {e}")
            return []

    def get_entity_by_id(self, table_name: str, entity_id: int) -> Optional[Any]:
        """Get a specific entity by ID"""
        table_class = self.table_classes.get(table_name)
        if not table_class:
            return None

        try:
            with Session(self.model.engine) as session:
                if table_name == "litography_notes":
                    # Notes don't have setting_id, just get by ID
                    from sqlalchemy.orm import joinedload
                    return (
                        session.query(table_class)
                        .options(joinedload(table_class.linked_node))
                        .filter_by(id=entity_id)
                        .first()
                    )
                else:
                    from sqlalchemy.orm import joinedload
                    
                    query = session.query(table_class).filter_by(id=entity_id, setting_id=self.setting_id)
                    
                    # Add eager loading for commonly accessed relationships
                    if table_name == "actor":
                        query = query.options(
                            joinedload(table_class.background),
                            joinedload(table_class.alignment),
                            joinedload(table_class.setting)
                        )
                    elif table_name == "faction":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    elif table_name == "location_":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    elif table_name == "object_":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    elif table_name == "history":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    elif table_name == "world_data":
                        query = query.options(
                            joinedload(table_class.setting)
                        )
                    
                    return query.first()
        except Exception as e:
            print(f"Error loading entity {entity_id} from {table_name}: {e}")
            return None

    def create_entity(self, table_name: str, **kwargs) -> Optional[Any]:
        """Create a new entity"""
        table_class = self.table_classes.get(table_name)
        if not table_class:
            return None

        try:
            # Add setting_id to the kwargs
            kwargs["setting_id"] = self.setting_id

            with Session(self.model.engine) as session:
                entity = table_class(**kwargs)
                session.add(entity)
                session.commit()
                session.refresh(entity)
                return entity
        except Exception as e:
            print(f"Error creating entity in {table_name}: {e}")
            return None

    def update_entity(self, entity: Any) -> bool:
        """Update an existing entity"""
        try:
            with Session(self.model.engine) as session:
                # Merge the entity into the session and commit
                session.merge(entity)
                session.commit()
                return True
        except Exception as e:
            print(f"Error updating entity: {e}")
            return False

    def delete_entity(self, entity: Any) -> bool:
        """Delete an entity"""
        try:
            with Session(self.model.engine) as session:
                # Re-attach the entity to the session and delete
                entity_to_delete = session.merge(entity)
                session.delete(entity_to_delete)
                session.commit()
                return True
        except Exception as e:
            print(f"Error deleting entity: {e}")
            return False

    def get_foreign_key_options(self, table_name: str, field_name: str) -> List[tuple]:
        """Get options for foreign key dropdowns"""
        # Map foreign key fields to their target tables
        fk_mappings = {
            "background_id": ("background", Background, "name"),
            "alignment_id": ("alignment", Alignment, "name"),
            "race_id": ("race", Race, "name"),
            "class_id": ("class", Class_, "name"),
            "faction_id": ("faction", Faction, "name"),
            "location_id": ("location_", Location, "name"),
            "actor_id": ("actor", Actor, "first_name"),  # Could combine first/last name
            "skill_id": ("skills", Skills, "name"),
            "object_id": ("object_", Object_, "name"),
        }

        if field_name not in fk_mappings:
            return []

        target_table, target_class, display_field = fk_mappings[field_name]

        try:
            with Session(self.model.engine) as session:
                entities = (
                    session.query(target_class)
                    .filter_by(setting_id=self.setting_id)
                    .all()
                )

                options = []
                for entity in entities:
                    display_value = getattr(entity, display_field, "")

                    # Special handling for actor names
                    if target_table == "actor" and hasattr(entity, "last_name"):
                        if entity.last_name:
                            display_value = f"{entity.first_name} {entity.last_name}"

                    options.append((entity.id, display_value or f"ID: {entity.id}"))

                return options
        except Exception as e:
            print(f"Error loading foreign key options for {field_name}: {e}")
            return []

    def get_relationship_entities(
        self, entity: Any, relationship_name: str
    ) -> List[Any]:
        """Get related entities for a given relationship"""
        try:
            with Session(self.model.engine) as session:
                # Re-attach entity to session
                entity = session.merge(entity)

                # Get relationships based on type
                if relationship_name == "actor_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        ActorAOnBRelations,
                    )

                    relations = (
                        session.query(ActorAOnBRelations)
                        .filter(
                            (ActorAOnBRelations.actor_a_id == entity.id)
                            | (ActorAOnBRelations.actor_b_id == entity.id)
                        )
                        .all()
                    )

                    related_entities = []
                    for rel in relations:
                        if rel.actor_a_id == entity.id:
                            related_entities.append(rel.actor_b)
                        else:
                            related_entities.append(rel.actor_a)
                    return related_entities

                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import (
                        FactionMembers,
                        Actor,
                        Faction,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Faction":
                        # Get actors who are members of this faction
                        memberships = (
                            session.query(FactionMembers)
                            .filter(FactionMembers.faction_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, membership.actor_id)
                            for membership in memberships
                            if membership.actor_id
                        ]
                    elif entity.__class__.__name__ == "Actor":
                        # Get factions this actor is a member of
                        memberships = (
                            session.query(FactionMembers)
                            .filter(FactionMembers.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Faction, membership.faction_id)
                            for membership in memberships
                            if membership.faction_id
                        ]

                elif relationship_name == "residents":
                    from storymaster.model.database.schema.base import (
                        Resident,
                        Actor,
                        Location,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Location":
                        # Get actors who live in this location
                        residencies = (
                            session.query(Resident)
                            .filter(Resident.location_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, residency.actor_id)
                            for residency in residencies
                            if residency.actor_id
                        ]
                    elif entity.__class__.__name__ == "Actor":
                        # Get locations where this actor lives
                        residencies = (
                            session.query(Resident)
                            .filter(Resident.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Location, residency.location_id)
                            for residency in residencies
                            if residency.location_id
                        ]
                elif relationship_name == "object_to_owner":
                    from storymaster.model.database.schema.base import (
                        ObjectToOwner,
                        Actor,
                        Object_,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Object_":
                        # Get actors who own this object
                        ownerships = (
                            session.query(ObjectToOwner)
                            .filter(ObjectToOwner.object_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, ownership.actor_id)
                            for ownership in ownerships
                            if ownership.actor_id
                        ]
                    elif entity.__class__.__name__ == "Actor":
                        # Get objects this actor owns
                        ownerships = (
                            session.query(ObjectToOwner)
                            .filter(ObjectToOwner.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Object_, ownership.object_id)
                            for ownership in ownerships
                            if ownership.object_id
                        ]

                elif relationship_name == "location_to_faction":
                    from storymaster.model.database.schema.base import (
                        LocationToFaction,
                        Location,
                        Faction,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Location":
                        # Get factions that control this location
                        controls = (
                            session.query(LocationToFaction)
                            .filter(LocationToFaction.location_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Faction, control.faction_id)
                            for control in controls
                            if control.faction_id
                        ]
                    elif entity.__class__.__name__ == "Faction":
                        # Get locations this faction controls
                        controls = (
                            session.query(LocationToFaction)
                            .filter(LocationToFaction.faction_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Location, control.location_id)
                            for control in controls
                            if control.location_id
                        ]

                elif relationship_name == "actor_to_skills":
                    from storymaster.model.database.schema.base import (
                        ActorToSkills,
                        Actor,
                        Skills,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Actor":
                        # Get skills this actor has
                        skill_relations = (
                            session.query(ActorToSkills)
                            .filter(ActorToSkills.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Skills, skill_rel.skill_id)
                            for skill_rel in skill_relations
                            if skill_rel.skill_id
                        ]
                    elif entity.__class__.__name__ == "Skills":
                        # Get actors who have this skill
                        skill_relations = (
                            session.query(ActorToSkills)
                            .filter(ActorToSkills.skill_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, skill_rel.actor_id)
                            for skill_rel in skill_relations
                            if skill_rel.actor_id
                        ]

                elif relationship_name == "actor_to_race":
                    from storymaster.model.database.schema.base import (
                        ActorToRace,
                        Actor,
                        Race,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Actor":
                        # Get races this actor belongs to
                        race_relations = (
                            session.query(ActorToRace)
                            .filter(ActorToRace.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Race, race_rel.race_id)
                            for race_rel in race_relations
                            if race_rel.race_id
                        ]
                    elif entity.__class__.__name__ == "Race":
                        # Get actors of this race
                        race_relations = (
                            session.query(ActorToRace)
                            .filter(ActorToRace.race_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, race_rel.actor_id)
                            for race_rel in race_relations
                            if race_rel.actor_id
                        ]

                elif relationship_name == "actor_to_class":
                    from storymaster.model.database.schema.base import (
                        ActorToClass,
                        Actor,
                        Class_,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Actor":
                        # Get classes this actor has
                        class_relations = (
                            session.query(ActorToClass)
                            .filter(ActorToClass.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Class_, class_rel.class_id)
                            for class_rel in class_relations
                            if class_rel.class_id
                        ]
                    elif entity.__class__.__name__ == "Class_":
                        # Get actors who have this class
                        class_relations = (
                            session.query(ActorToClass)
                            .filter(ActorToClass.class_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, class_rel.actor_id)
                            for class_rel in class_relations
                            if class_rel.actor_id
                        ]

                elif relationship_name == "actor_to_stat":
                    from storymaster.model.database.schema.base import (
                        ActorToStat,
                        Actor,
                        Stat,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Actor":
                        # Get stats this actor has
                        stat_relations = (
                            session.query(ActorToStat)
                            .filter(ActorToStat.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Stat, stat_rel.stat_id)
                            for stat_rel in stat_relations
                            if stat_rel.stat_id
                        ]
                    elif entity.__class__.__name__ == "Stat":
                        # Get actors who have this stat
                        stat_relations = (
                            session.query(ActorToStat)
                            .filter(ActorToStat.stat_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, stat_rel.actor_id)
                            for stat_rel in stat_relations
                            if stat_rel.actor_id
                        ]

                elif relationship_name == "history_actor":
                    from storymaster.model.database.schema.base import (
                        HistoryActor,
                        Actor,
                        History,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Actor":
                        # Get historical events this actor was involved in
                        history_relations = (
                            session.query(HistoryActor)
                            .filter(HistoryActor.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(History, hist_rel.history_id)
                            for hist_rel in history_relations
                            if hist_rel.history_id
                        ]
                    elif entity.__class__.__name__ == "History":
                        # Get actors involved in this historical event
                        history_relations = (
                            session.query(HistoryActor)
                            .filter(HistoryActor.history_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, hist_rel.actor_id)
                            for hist_rel in history_relations
                            if hist_rel.actor_id
                        ]

                elif relationship_name == "faction_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        FactionAOnBRelations,
                        Faction,
                    )

                    # Query database directly for fresh data
                    relations = (
                        session.query(FactionAOnBRelations)
                        .filter(
                            (FactionAOnBRelations.faction_a_id == entity.id)
                            | (FactionAOnBRelations.faction_b_id == entity.id)
                        )
                        .all()
                    )

                    related_entities = []
                    for rel in relations:
                        if rel.faction_a_id == entity.id:
                            related_entities.append(
                                session.get(Faction, rel.faction_b_id)
                            )
                        else:
                            related_entities.append(
                                session.get(Faction, rel.faction_a_id)
                            )
                    return [entity for entity in related_entities if entity is not None]

                elif relationship_name == "history_faction":
                    from storymaster.model.database.schema.base import (
                        HistoryFaction,
                        Faction,
                        History,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Faction":
                        # Get historical events this faction was involved in
                        history_relations = (
                            session.query(HistoryFaction)
                            .filter(HistoryFaction.faction_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(History, hist_rel.history_id)
                            for hist_rel in history_relations
                            if hist_rel.history_id
                        ]
                    elif entity.__class__.__name__ == "History":
                        # Get factions involved in this historical event
                        history_relations = (
                            session.query(HistoryFaction)
                            .filter(HistoryFaction.history_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Faction, hist_rel.faction_id)
                            for hist_rel in history_relations
                            if hist_rel.faction_id
                        ]

                elif relationship_name == "location_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        LocationAOnBRelations,
                        Location,
                    )

                    # Query database directly for fresh data
                    relations = (
                        session.query(LocationAOnBRelations)
                        .filter(
                            (LocationAOnBRelations.location_a_id == entity.id)
                            | (LocationAOnBRelations.location_b_id == entity.id)
                        )
                        .all()
                    )

                    related_entities = []
                    for rel in relations:
                        if rel.location_a_id == entity.id:
                            related_entities.append(
                                session.get(Location, rel.location_b_id)
                            )
                        else:
                            related_entities.append(
                                session.get(Location, rel.location_a_id)
                            )
                    return [entity for entity in related_entities if entity is not None]

                elif relationship_name == "location_geographic_relations":
                    from storymaster.model.database.schema.base import (
                        LocationGeographicRelations,
                        Location,
                    )

                    # Query database directly for fresh data
                    relations = (
                        session.query(LocationGeographicRelations)
                        .filter(
                            (LocationGeographicRelations.location_a_id == entity.id)
                            | (LocationGeographicRelations.location_b_id == entity.id)
                        )
                        .all()
                    )

                    related_entities = []
                    for rel in relations:
                        if rel.location_a_id == entity.id:
                            related_entities.append(
                                session.get(Location, rel.location_b_id)
                            )
                        else:
                            related_entities.append(
                                session.get(Location, rel.location_a_id)
                            )
                    return [entity for entity in related_entities if entity is not None]

                elif relationship_name == "location_political_relations":
                    from storymaster.model.database.schema.base import (
                        LocationPoliticalRelations,
                        Location,
                    )

                    # Query database directly for fresh data
                    relations = (
                        session.query(LocationPoliticalRelations)
                        .filter(
                            (LocationPoliticalRelations.location_a_id == entity.id)
                            | (LocationPoliticalRelations.location_b_id == entity.id)
                        )
                        .all()
                    )

                    related_entities = []
                    for rel in relations:
                        if rel.location_a_id == entity.id:
                            related_entities.append(
                                session.get(Location, rel.location_b_id)
                            )
                        else:
                            related_entities.append(
                                session.get(Location, rel.location_a_id)
                            )
                    return [entity for entity in related_entities if entity is not None]

                elif relationship_name == "location_economic_relations":
                    from storymaster.model.database.schema.base import (
                        LocationEconomicRelations,
                        Location,
                    )

                    # Query database directly for fresh data
                    relations = (
                        session.query(LocationEconomicRelations)
                        .filter(
                            (LocationEconomicRelations.location_a_id == entity.id)
                            | (LocationEconomicRelations.location_b_id == entity.id)
                        )
                        .all()
                    )

                    related_entities = []
                    for rel in relations:
                        if rel.location_a_id == entity.id:
                            related_entities.append(
                                session.get(Location, rel.location_b_id)
                            )
                        else:
                            related_entities.append(
                                session.get(Location, rel.location_a_id)
                            )
                    return [entity for entity in related_entities if entity is not None]

                elif relationship_name == "location_hierarchy":
                    from storymaster.model.database.schema.base import (
                        LocationHierarchy,
                        Location,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Location":
                        # Get both parent and child locations
                        parent_relations = (
                            session.query(LocationHierarchy)
                            .filter(LocationHierarchy.child_location_id == entity.id)
                            .all()
                        )
                        child_relations = (
                            session.query(LocationHierarchy)
                            .filter(LocationHierarchy.parent_location_id == entity.id)
                            .all()
                        )

                        related_entities = []
                        # Add parent locations
                        for rel in parent_relations:
                            related_entities.append(
                                session.get(Location, rel.parent_location_id)
                            )
                        # Add child locations
                        for rel in child_relations:
                            related_entities.append(
                                session.get(Location, rel.child_location_id)
                            )

                        return [
                            entity for entity in related_entities if entity is not None
                        ]

                elif relationship_name == "location_city_districts":
                    from storymaster.model.database.schema.base import (
                        LocationCityDistricts,
                        Location,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Location":
                        # Get districts in this city or cities this location is a district of
                        city_relations = (
                            session.query(LocationCityDistricts)
                            .filter(LocationCityDistricts.location_id == entity.id)
                            .all()
                        )
                        district_relations = (
                            session.query(LocationCityDistricts)
                            .filter(LocationCityDistricts.district_id == entity.id)
                            .all()
                        )

                        related_entities = []
                        # Add districts of this city
                        for rel in city_relations:
                            if rel.district_id:
                                related_entities.append(
                                    session.get(Location, rel.district_id)
                                )
                        # Add cities this location is a district of
                        for rel in district_relations:
                            if rel.location_id:
                                related_entities.append(
                                    session.get(Location, rel.location_id)
                                )

                        return [
                            entity for entity in related_entities if entity is not None
                        ]

                elif relationship_name == "location_flora_fauna":
                    from storymaster.model.database.schema.base import (
                        LocationFloraFauna,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "Location":
                        # Get flora/fauna entries for this location
                        flora_fauna_entries = (
                            session.query(LocationFloraFauna)
                            .filter(LocationFloraFauna.location_id == entity.id)
                            .all()
                        )

                        return flora_fauna_entries

                elif relationship_name == "litography_note_to_world_data":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToWorldData,
                        WorldData,
                        LitographyNotes,
                    )

                    # Query database directly for fresh data
                    if entity.__class__.__name__ == "LitographyNotes":
                        # Get lore entries associated with this note
                        note_relations = (
                            session.query(LitographyNoteToWorldData)
                            .filter(LitographyNoteToWorldData.note_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(WorldData, rel.world_data_id)
                            for rel in note_relations
                            if rel.world_data_id
                        ]
                    elif entity.__class__.__name__ == "WorldData":
                        # Get notes associated with this lore entry
                        note_relations = (
                            session.query(LitographyNoteToWorldData)
                            .filter(
                                LitographyNoteToWorldData.world_data_id == entity.id
                            )
                            .all()
                        )
                        return [
                            session.get(LitographyNotes, rel.note_id)
                            for rel in note_relations
                            if rel.note_id
                        ]

                elif relationship_name == "litography_note_to_actor":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToActor,
                        Actor,
                        LitographyNotes,
                    )

                    if entity.__class__.__name__ == "LitographyNotes":
                        note_relations = (
                            session.query(LitographyNoteToActor)
                            .filter(LitographyNoteToActor.note_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Actor, rel.actor_id)
                            for rel in note_relations
                            if rel.actor_id
                        ]
                    elif entity.__class__.__name__ == "Actor":
                        note_relations = (
                            session.query(LitographyNoteToActor)
                            .filter(LitographyNoteToActor.actor_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(LitographyNotes, rel.note_id)
                            for rel in note_relations
                            if rel.note_id
                        ]

                elif relationship_name == "litography_note_to_location":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToLocation,
                        Location,
                        LitographyNotes,
                    )

                    if entity.__class__.__name__ == "LitographyNotes":
                        note_relations = (
                            session.query(LitographyNoteToLocation)
                            .filter(LitographyNoteToLocation.note_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Location, rel.location_id)
                            for rel in note_relations
                            if rel.location_id
                        ]
                    elif entity.__class__.__name__ == "Location":
                        note_relations = (
                            session.query(LitographyNoteToLocation)
                            .filter(LitographyNoteToLocation.location_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(LitographyNotes, rel.note_id)
                            for rel in note_relations
                            if rel.note_id
                        ]

                elif relationship_name == "litography_note_to_object":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToObject,
                        Object_,
                        LitographyNotes,
                    )

                    if entity.__class__.__name__ == "LitographyNotes":
                        note_relations = (
                            session.query(LitographyNoteToObject)
                            .filter(LitographyNoteToObject.note_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Object_, rel.object_id)
                            for rel in note_relations
                            if rel.object_id
                        ]
                    elif entity.__class__.__name__ == "Object_":
                        note_relations = (
                            session.query(LitographyNoteToObject)
                            .filter(LitographyNoteToObject.object_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(LitographyNotes, rel.note_id)
                            for rel in note_relations
                            if rel.note_id
                        ]

                elif relationship_name == "litography_note_to_faction":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToFaction,
                        Faction,
                        LitographyNotes,
                    )

                    if entity.__class__.__name__ == "LitographyNotes":
                        note_relations = (
                            session.query(LitographyNoteToFaction)
                            .filter(LitographyNoteToFaction.note_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(Faction, rel.faction_id)
                            for rel in note_relations
                            if rel.faction_id
                        ]
                    elif entity.__class__.__name__ == "Faction":
                        note_relations = (
                            session.query(LitographyNoteToFaction)
                            .filter(LitographyNoteToFaction.faction_id == entity.id)
                            .all()
                        )
                        return [
                            session.get(LitographyNotes, rel.note_id)
                            for rel in note_relations
                            if rel.note_id
                        ]

                # Add more relationship types as needed
                return []

        except Exception as e:
            print(f"Error getting relationship entities for {relationship_name}: {e}")
            return []

    def add_relationship(
        self,
        entity: Any,
        relationship_name: str,
        related_entity: Any,
        relationship_data: dict = None,
    ) -> bool:
        """Add a relationship between entities"""
        try:
            with Session(self.model.engine) as session:
                # Re-attach entities to session
                entity = session.merge(entity)
                related_entity = session.merge(related_entity)

                # Create relationship based on type
                if relationship_name == "actor_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        ActorAOnBRelations,
                    )

                    # Check if relationship already exists
                    existing = (
                        session.query(ActorAOnBRelations)
                        .filter(
                            (
                                (ActorAOnBRelations.actor_a_id == entity.id)
                                & (ActorAOnBRelations.actor_b_id == related_entity.id)
                            )
                            | (
                                (ActorAOnBRelations.actor_a_id == related_entity.id)
                                & (ActorAOnBRelations.actor_b_id == entity.id)
                            )
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new relationship
                    new_relation = ActorAOnBRelations(
                        actor_a_id=entity.id,
                        actor_b_id=related_entity.id,
                        setting_id=self.setting_id,
                        overall=(
                            relationship_data.get("description", "")
                            if relationship_data
                            else ""
                        ),
                        power_dynamic=(
                            relationship_data.get("relationship_type", "")
                            if relationship_data
                            else ""
                        ),
                    )
                    session.add(new_relation)

                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers

                    # Check if membership already exists
                    existing = (
                        session.query(FactionMembers)
                        .filter(
                            (FactionMembers.actor_id == entity.id)
                            & (FactionMembers.faction_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Membership already exists

                    # Create new membership
                    new_membership = FactionMembers(
                        actor_id=entity.id,
                        faction_id=related_entity.id,
                        setting_id=self.setting_id,
                        actor_role=(
                            relationship_data.get("role", "")
                            if relationship_data
                            else ""
                        ),
                        relative_power=(
                            relationship_data.get("rank", 1) if relationship_data else 1
                        ),
                    )
                    session.add(new_membership)

                elif relationship_name == "residents":
                    from storymaster.model.database.schema.base import Resident

                    # Check if residency already exists
                    existing = (
                        session.query(Resident)
                        .filter(
                            (Resident.actor_id == entity.id)
                            & (Resident.location_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Residency already exists

                    # Create new residency
                    new_residency = Resident(
                        actor_id=entity.id,
                        location_id=related_entity.id,
                        setting_id=self.setting_id,
                    )
                    session.add(new_residency)

                elif relationship_name == "object_to_owner":
                    from storymaster.model.database.schema.base import ObjectToOwner

                    # Check if ownership already exists
                    existing = (
                        session.query(ObjectToOwner)
                        .filter(
                            (ObjectToOwner.actor_id == entity.id)
                            & (ObjectToOwner.object_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Ownership already exists

                    # Create new ownership
                    new_ownership = ObjectToOwner(
                        actor_id=entity.id,
                        object_id=related_entity.id,
                        setting_id=self.setting_id,
                    )
                    session.add(new_ownership)

                elif relationship_name == "location_to_faction":
                    from storymaster.model.database.schema.base import LocationToFaction

                    # Check if control already exists
                    existing = (
                        session.query(LocationToFaction)
                        .filter(
                            (LocationToFaction.location_id == entity.id)
                            & (LocationToFaction.faction_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Control already exists

                    # Create new control
                    new_control = LocationToFaction(
                        location_id=entity.id,
                        faction_id=related_entity.id,
                        setting_id=self.setting_id,
                    )
                    session.add(new_control)

                elif relationship_name == "actor_to_skills":
                    from storymaster.model.database.schema.base import ActorToSkills

                    # Check if skill relation already exists
                    existing = (
                        session.query(ActorToSkills)
                        .filter(
                            (ActorToSkills.actor_id == entity.id)
                            & (ActorToSkills.skill_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Skill relation already exists

                    # Create new skill relation
                    new_skill_relation = ActorToSkills(
                        actor_id=entity.id,
                        skill_id=related_entity.id,
                        setting_id=self.setting_id,
                        skill_level=1,  # Default skill level
                    )
                    session.add(new_skill_relation)

                elif relationship_name == "actor_to_race":
                    from storymaster.model.database.schema.base import ActorToRace

                    # Check if race relation already exists
                    existing = (
                        session.query(ActorToRace)
                        .filter(
                            (ActorToRace.actor_id == entity.id)
                            & (ActorToRace.race_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Race relation already exists

                    # Create new race relation
                    new_race_relation = ActorToRace(
                        actor_id=entity.id,
                        race_id=related_entity.id,
                        setting_id=self.setting_id,
                    )
                    session.add(new_race_relation)

                elif relationship_name == "actor_to_class":
                    from storymaster.model.database.schema.base import ActorToClass

                    # Check if class relation already exists
                    existing = (
                        session.query(ActorToClass)
                        .filter(
                            (ActorToClass.actor_id == entity.id)
                            & (ActorToClass.class_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Class relation already exists

                    # Create new class relation
                    new_class_relation = ActorToClass(
                        actor_id=entity.id,
                        class_id=related_entity.id,
                        setting_id=self.setting_id,
                        level=1,  # Default level
                    )
                    session.add(new_class_relation)

                elif relationship_name == "actor_to_stat":
                    from storymaster.model.database.schema.base import ActorToStat

                    # Check if stat relation already exists
                    existing = (
                        session.query(ActorToStat)
                        .filter(
                            (ActorToStat.actor_id == entity.id)
                            & (ActorToStat.stat_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Stat relation already exists

                    # Create new stat relation
                    new_stat_relation = ActorToStat(
                        actor_id=entity.id,
                        stat_id=related_entity.id,
                        setting_id=self.setting_id,
                        stat_value=10,  # Default stat value
                    )
                    session.add(new_stat_relation)

                elif relationship_name == "history_actor":
                    from storymaster.model.database.schema.base import HistoryActor

                    # Check if history relation already exists
                    existing = (
                        session.query(HistoryActor)
                        .filter(
                            (HistoryActor.actor_id == entity.id)
                            & (HistoryActor.history_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # History relation already exists

                    # Create new history relation
                    new_history_relation = HistoryActor(
                        actor_id=entity.id,
                        history_id=related_entity.id,
                        setting_id=self.setting_id,
                    )
                    session.add(new_history_relation)

                elif relationship_name == "faction_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        FactionAOnBRelations,
                    )

                    # Check if relationship already exists
                    existing = (
                        session.query(FactionAOnBRelations)
                        .filter(
                            (
                                (FactionAOnBRelations.faction_a_id == entity.id)
                                & (
                                    FactionAOnBRelations.faction_b_id
                                    == related_entity.id
                                )
                            )
                            | (
                                (FactionAOnBRelations.faction_a_id == related_entity.id)
                                & (FactionAOnBRelations.faction_b_id == entity.id)
                            )
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new relationship
                    new_relation = FactionAOnBRelations(
                        faction_a_id=entity.id,
                        faction_b_id=related_entity.id,
                        setting_id=self.setting_id,
                        description=(
                            relationship_data.get("description", "")
                            if relationship_data
                            else ""
                        ),
                        relationship_type=(
                            relationship_data.get("relationship_type", "")
                            if relationship_data
                            else ""
                        ),
                        status=(
                            relationship_data.get("status", "")
                            if relationship_data
                            else ""
                        ),
                        strength=(
                            relationship_data.get("strength", 5)
                            if relationship_data
                            else 5
                        ),
                        trust_level=(
                            relationship_data.get("trust_level", 5)
                            if relationship_data
                            else 5
                        ),
                        is_mutual=(
                            relationship_data.get("is_mutual", True)
                            if relationship_data
                            else True
                        ),
                        is_public=(
                            relationship_data.get("is_public", True)
                            if relationship_data
                            else True
                        ),
                        overall=(
                            relationship_data.get("overall", "")
                            if relationship_data
                            else ""
                        ),
                        economically=(
                            relationship_data.get("economically", "")
                            if relationship_data
                            else ""
                        ),
                        politically=(
                            relationship_data.get("politically", "")
                            if relationship_data
                            else ""
                        ),
                        opinion=(
                            relationship_data.get("opinion", "")
                            if relationship_data
                            else ""
                        ),
                    )
                    session.add(new_relation)

                elif relationship_name == "history_faction":
                    from storymaster.model.database.schema.base import HistoryFaction

                    # Check if history relation already exists
                    existing = (
                        session.query(HistoryFaction)
                        .filter(
                            (HistoryFaction.faction_id == entity.id)
                            & (HistoryFaction.history_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # History relation already exists

                    # Create new history relation
                    new_history_relation = HistoryFaction(
                        faction_id=entity.id,
                        history_id=related_entity.id,
                        setting_id=self.setting_id,
                        role_in_event=(
                            relationship_data.get("role_in_event", "")
                            if relationship_data
                            else ""
                        ),
                        involvement_level=(
                            relationship_data.get("involvement_level", "")
                            if relationship_data
                            else ""
                        ),
                        impact_on_faction=(
                            relationship_data.get("impact_on_faction", "")
                            if relationship_data
                            else ""
                        ),
                        faction_perspective=(
                            relationship_data.get("faction_perspective", "")
                            if relationship_data
                            else ""
                        ),
                        consequences=(
                            relationship_data.get("consequences", "")
                            if relationship_data
                            else ""
                        ),
                    )
                    session.add(new_history_relation)

                elif relationship_name == "location_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        LocationAOnBRelations,
                    )

                    # Check if relationship already exists
                    existing = (
                        session.query(LocationAOnBRelations)
                        .filter(
                            (
                                (LocationAOnBRelations.location_a_id == entity.id)
                                & (
                                    LocationAOnBRelations.location_b_id
                                    == related_entity.id
                                )
                            )
                            | (
                                (
                                    LocationAOnBRelations.location_a_id
                                    == related_entity.id
                                )
                                & (LocationAOnBRelations.location_b_id == entity.id)
                            )
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new relationship
                    new_relation = LocationAOnBRelations(
                        location_a_id=entity.id,
                        location_b_id=related_entity.id,
                        setting_id=self.setting_id,
                        description=(
                            relationship_data.get("description", "")
                            if relationship_data
                            else ""
                        ),
                        relationship_type=(
                            relationship_data.get("relationship_type", "")
                            if relationship_data
                            else ""
                        ),
                        status=(
                            relationship_data.get("status", "")
                            if relationship_data
                            else ""
                        ),
                        strength=(
                            relationship_data.get("strength", 5)
                            if relationship_data
                            else 5
                        ),
                        is_mutual=(
                            relationship_data.get("is_mutual", True)
                            if relationship_data
                            else True
                        ),
                        is_public=(
                            relationship_data.get("is_public", True)
                            if relationship_data
                            else True
                        ),
                    )
                    session.add(new_relation)

                elif relationship_name == "location_geographic_relations":
                    from storymaster.model.database.schema.base import (
                        LocationGeographicRelations,
                    )

                    # Check if relationship already exists
                    existing = (
                        session.query(LocationGeographicRelations)
                        .filter(
                            (
                                (LocationGeographicRelations.location_a_id == entity.id)
                                & (
                                    LocationGeographicRelations.location_b_id
                                    == related_entity.id
                                )
                            )
                            | (
                                (
                                    LocationGeographicRelations.location_a_id
                                    == related_entity.id
                                )
                                & (
                                    LocationGeographicRelations.location_b_id
                                    == entity.id
                                )
                            )
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new geographic relationship
                    new_relation = LocationGeographicRelations(
                        location_a_id=entity.id,
                        location_b_id=related_entity.id,
                        setting_id=self.setting_id,
                        geographic_type=(
                            relationship_data.get("geographic_type", "")
                            if relationship_data
                            else ""
                        ),
                        distance=(
                            relationship_data.get("distance", "")
                            if relationship_data
                            else ""
                        ),
                        travel_time=(
                            relationship_data.get("travel_time", "")
                            if relationship_data
                            else ""
                        ),
                        travel_difficulty=(
                            relationship_data.get("travel_difficulty", "")
                            if relationship_data
                            else ""
                        ),
                        travel_method=(
                            relationship_data.get("travel_method", "")
                            if relationship_data
                            else ""
                        ),
                        description=(
                            relationship_data.get("description", "")
                            if relationship_data
                            else ""
                        ),
                    )
                    session.add(new_relation)

                elif relationship_name == "location_political_relations":
                    from storymaster.model.database.schema.base import (
                        LocationPoliticalRelations,
                    )

                    # Check if relationship already exists
                    existing = (
                        session.query(LocationPoliticalRelations)
                        .filter(
                            (
                                (LocationPoliticalRelations.location_a_id == entity.id)
                                & (
                                    LocationPoliticalRelations.location_b_id
                                    == related_entity.id
                                )
                            )
                            | (
                                (
                                    LocationPoliticalRelations.location_a_id
                                    == related_entity.id
                                )
                                & (
                                    LocationPoliticalRelations.location_b_id
                                    == entity.id
                                )
                            )
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new political relationship
                    new_relation = LocationPoliticalRelations(
                        location_a_id=entity.id,
                        location_b_id=related_entity.id,
                        setting_id=self.setting_id,
                        political_type=(
                            relationship_data.get("political_type", "")
                            if relationship_data
                            else ""
                        ),
                        treaty_name=(
                            relationship_data.get("treaty_name", "")
                            if relationship_data
                            else ""
                        ),
                        treaty_date=(
                            relationship_data.get("treaty_date", "")
                            if relationship_data
                            else ""
                        ),
                        status=(
                            relationship_data.get("status", "")
                            if relationship_data
                            else ""
                        ),
                        description=(
                            relationship_data.get("description", "")
                            if relationship_data
                            else ""
                        ),
                    )
                    session.add(new_relation)

                elif relationship_name == "location_economic_relations":
                    from storymaster.model.database.schema.base import (
                        LocationEconomicRelations,
                    )

                    # Check if relationship already exists
                    existing = (
                        session.query(LocationEconomicRelations)
                        .filter(
                            (
                                (LocationEconomicRelations.location_a_id == entity.id)
                                & (
                                    LocationEconomicRelations.location_b_id
                                    == related_entity.id
                                )
                            )
                            | (
                                (
                                    LocationEconomicRelations.location_a_id
                                    == related_entity.id
                                )
                                & (LocationEconomicRelations.location_b_id == entity.id)
                            )
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new economic relationship
                    new_relation = LocationEconomicRelations(
                        location_a_id=entity.id,
                        location_b_id=related_entity.id,
                        setting_id=self.setting_id,
                        economic_type=(
                            relationship_data.get("economic_type", "")
                            if relationship_data
                            else ""
                        ),
                        trade_goods=(
                            relationship_data.get("trade_goods", "")
                            if relationship_data
                            else ""
                        ),
                        trade_volume=(
                            relationship_data.get("trade_volume", "")
                            if relationship_data
                            else ""
                        ),
                        trade_frequency=(
                            relationship_data.get("trade_frequency", "")
                            if relationship_data
                            else ""
                        ),
                        trade_value=(
                            relationship_data.get("trade_value", "")
                            if relationship_data
                            else ""
                        ),
                        description=(
                            relationship_data.get("description", "")
                            if relationship_data
                            else ""
                        ),
                    )
                    session.add(new_relation)

                elif relationship_name == "location_hierarchy":
                    from storymaster.model.database.schema.base import LocationHierarchy

                    # Check if relationship already exists
                    existing = (
                        session.query(LocationHierarchy)
                        .filter(
                            (LocationHierarchy.parent_location_id == entity.id)
                            & (LocationHierarchy.child_location_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new hierarchy relationship (entity is parent, related_entity is child)
                    new_relation = LocationHierarchy(
                        parent_location_id=entity.id,
                        child_location_id=related_entity.id,
                        setting_id=self.setting_id,
                        hierarchy_type=(
                            relationship_data.get("hierarchy_type", "")
                            if relationship_data
                            else ""
                        ),
                        parent_type=(
                            relationship_data.get("parent_type", "")
                            if relationship_data
                            else ""
                        ),
                        child_type=(
                            relationship_data.get("child_type", "")
                            if relationship_data
                            else ""
                        ),
                        administrative_level=(
                            relationship_data.get("administrative_level", 1)
                            if relationship_data
                            else 1
                        ),
                        governance_type=(
                            relationship_data.get("governance_type", "")
                            if relationship_data
                            else ""
                        ),
                        description=(
                            relationship_data.get("description", "")
                            if relationship_data
                            else ""
                        ),
                    )
                    session.add(new_relation)

                elif relationship_name == "location_city_districts":
                    from storymaster.model.database.schema.base import (
                        LocationCityDistricts,
                    )

                    # Check if relationship already exists
                    existing = (
                        session.query(LocationCityDistricts)
                        .filter(
                            (LocationCityDistricts.location_id == entity.id)
                            & (LocationCityDistricts.district_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new district relationship (entity is city, related_entity is district)
                    new_relation = LocationCityDistricts(
                        location_id=entity.id,
                        district_id=related_entity.id,
                        setting_id=self.setting_id,
                    )
                    session.add(new_relation)

                elif relationship_name == "location_flora_fauna":
                    from storymaster.model.database.schema.base import (
                        LocationFloraFauna,
                    )

                    # For flora/fauna, we're adding a new entry, not linking to another entity
                    # The related_entity in this case would be the data for the flora/fauna
                    new_flora_fauna = LocationFloraFauna(
                        location_id=entity.id,
                        setting_id=self.setting_id,
                        name=(
                            relationship_data.get("name", "")
                            if relationship_data
                            else ""
                        ),
                        description=(
                            relationship_data.get("description", "")
                            if relationship_data
                            else ""
                        ),
                        living_type=(
                            relationship_data.get("living_type", "")
                            if relationship_data
                            else ""
                        ),
                    )
                    session.add(new_flora_fauna)

                elif relationship_name == "litography_note_to_world_data":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToWorldData,
                    )

                    # Check if relationship already exists
                    existing = (
                        session.query(LitographyNoteToWorldData)
                        .filter(
                            (LitographyNoteToWorldData.note_id == entity.id)
                            & (
                                LitographyNoteToWorldData.world_data_id
                                == related_entity.id
                            )
                        )
                        .first()
                    )

                    if existing:
                        return False  # Relationship already exists

                    # Create new note-to-lore relationship
                    new_relation = LitographyNoteToWorldData(
                        note_id=entity.id, world_data_id=related_entity.id
                    )
                    session.add(new_relation)

                elif relationship_name == "litography_note_to_actor":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToActor,
                    )

                    existing = (
                        session.query(LitographyNoteToActor)
                        .filter(
                            (LitographyNoteToActor.note_id == entity.id)
                            & (LitographyNoteToActor.actor_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False

                    new_relation = LitographyNoteToActor(
                        note_id=entity.id, actor_id=related_entity.id
                    )
                    session.add(new_relation)

                elif relationship_name == "litography_note_to_location":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToLocation,
                    )

                    existing = (
                        session.query(LitographyNoteToLocation)
                        .filter(
                            (LitographyNoteToLocation.note_id == entity.id)
                            & (
                                LitographyNoteToLocation.location_id
                                == related_entity.id
                            )
                        )
                        .first()
                    )

                    if existing:
                        return False

                    new_relation = LitographyNoteToLocation(
                        note_id=entity.id, location_id=related_entity.id
                    )
                    session.add(new_relation)

                elif relationship_name == "litography_note_to_object":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToObject,
                    )

                    existing = (
                        session.query(LitographyNoteToObject)
                        .filter(
                            (LitographyNoteToObject.note_id == entity.id)
                            & (LitographyNoteToObject.object_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False

                    new_relation = LitographyNoteToObject(
                        note_id=entity.id, object_id=related_entity.id
                    )
                    session.add(new_relation)

                elif relationship_name == "litography_note_to_faction":
                    from storymaster.model.database.schema.base import (
                        LitographyNoteToFaction,
                    )

                    existing = (
                        session.query(LitographyNoteToFaction)
                        .filter(
                            (LitographyNoteToFaction.note_id == entity.id)
                            & (LitographyNoteToFaction.faction_id == related_entity.id)
                        )
                        .first()
                    )

                    if existing:
                        return False

                    new_relation = LitographyNoteToFaction(
                        note_id=entity.id, faction_id=related_entity.id
                    )
                    session.add(new_relation)

                # Add more relationship types as needed

                session.commit()
                return True

        except Exception as e:
            print(f"Error adding relationship {relationship_name}: {e}")
            return False

    def remove_relationship(
        self, entity: Any, relationship_name: str, related_entity: Any
    ) -> bool:
        """Remove a relationship between entities"""
        try:
            with Session(self.model.engine) as session:
                # Remove relationship based on type
                if relationship_name == "actor_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        ActorAOnBRelations,
                    )

                    relation = (
                        session.query(ActorAOnBRelations)
                        .filter(
                            (
                                (ActorAOnBRelations.actor_a_id == entity.id)
                                & (ActorAOnBRelations.actor_b_id == related_entity.id)
                            )
                            | (
                                (ActorAOnBRelations.actor_a_id == related_entity.id)
                                & (ActorAOnBRelations.actor_b_id == entity.id)
                            )
                        )
                        .first()
                    )

                    if relation:
                        session.delete(relation)

                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers

                    membership = (
                        session.query(FactionMembers)
                        .filter(
                            (FactionMembers.actor_id == entity.id)
                            & (FactionMembers.faction_id == related_entity.id)
                        )
                        .first()
                    )

                    if membership:
                        session.delete(membership)

                elif relationship_name == "residents":
                    from storymaster.model.database.schema.base import Resident

                    residency = (
                        session.query(Resident)
                        .filter(
                            (Resident.actor_id == entity.id)
                            & (Resident.location_id == related_entity.id)
                        )
                        .first()
                    )

                    if residency:
                        session.delete(residency)

                # Add more relationship types as needed

                session.commit()
                return True

        except Exception as e:
            print(f"Error removing relationship {relationship_name}: {e}")
            return False

    def update_relationship(
        self,
        entity: Any,
        relationship_name: str,
        related_entity: Any,
        relationship_data: dict,
    ) -> bool:
        """Update an existing relationship with new data"""
        try:
            with Session(self.model.engine) as session:
                # Update relationship based on type
                if relationship_name == "actor_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        ActorAOnBRelations,
                    )

                    relation = (
                        session.query(ActorAOnBRelations)
                        .filter(
                            (
                                (ActorAOnBRelations.actor_a_id == entity.id)
                                & (ActorAOnBRelations.actor_b_id == related_entity.id)
                            )
                            | (
                                (ActorAOnBRelations.actor_a_id == related_entity.id)
                                & (ActorAOnBRelations.actor_b_id == entity.id)
                            )
                        )
                        .first()
                    )

                    if relation:
                        # Map relationship data to dedicated database columns
                        relation.description = relationship_data.get("description")
                        relation.notes = relationship_data.get("notes")
                        relation.timeline = relationship_data.get("timeline")
                        relation.relationship_type = relationship_data.get(
                            "relationship_type"
                        )
                        relation.status = relationship_data.get("status")
                        relation.strength = relationship_data.get("strength")
                        relation.trust_level = relationship_data.get("trust_level")
                        relation.is_mutual = relationship_data.get("is_mutual", True)
                        relation.is_public = relationship_data.get("is_public", True)
                        relation.how_met = relationship_data.get("how_met")
                        relation.shared_history = relationship_data.get(
                            "shared_history"
                        )
                        relation.current_status = relationship_data.get(
                            "current_status"
                        )

                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers

                    membership = (
                        session.query(FactionMembers)
                        .filter(
                            (FactionMembers.actor_id == entity.id)
                            & (FactionMembers.faction_id == related_entity.id)
                        )
                        .first()
                    )

                    if membership:
                        # Map membership data to dedicated database columns
                        membership.role = relationship_data.get("role")
                        membership.rank = relationship_data.get("rank")
                        membership.membership_status = relationship_data.get(
                            "membership_status"
                        )
                        membership.responsibilities = relationship_data.get(
                            "responsibilities"
                        )
                        membership.loyalty = relationship_data.get("loyalty")
                        membership.join_date = relationship_data.get("join_date")

                # Add more relationship types as needed

                session.commit()
                return True

        except Exception as e:
            print(f"Error updating relationship {relationship_name}: {e}")
            return False

    def get_relationship_data(
        self, entity: Any, relationship_name: str, related_entity: Any
    ) -> dict:
        """Get relationship data for editing"""
        try:
            with Session(self.model.engine) as session:
                if relationship_name == "actor_a_on_b_relations":
                    from storymaster.model.database.schema.base import (
                        ActorAOnBRelations,
                    )

                    relation = (
                        session.query(ActorAOnBRelations)
                        .filter(
                            (
                                (ActorAOnBRelations.actor_a_id == entity.id)
                                & (ActorAOnBRelations.actor_b_id == related_entity.id)
                            )
                            | (
                                (ActorAOnBRelations.actor_a_id == related_entity.id)
                                & (ActorAOnBRelations.actor_b_id == entity.id)
                            )
                        )
                        .first()
                    )

                    if relation:
                        return {
                            # New structured fields
                            "description": relation.description or "",
                            "notes": relation.notes or "",
                            "timeline": relation.timeline or "",
                            "relationship_type": relation.relationship_type or "",
                            "status": relation.status or "",
                            "strength": relation.strength or 5,
                            "trust_level": relation.trust_level or 5,
                            "is_mutual": (
                                relation.is_mutual
                                if relation.is_mutual is not None
                                else True
                            ),
                            "is_public": (
                                relation.is_public
                                if relation.is_public is not None
                                else True
                            ),
                            "how_met": relation.how_met or "",
                            "shared_history": relation.shared_history or "",
                            "current_status": relation.current_status or "",
                            # Legacy fields (for backward compatibility)
                            "overall": relation.overall or "",
                            "power_dynamic": relation.power_dynamic or "",
                            "economically": relation.economically or "",
                        }

                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers

                    membership = (
                        session.query(FactionMembers)
                        .filter(
                            (FactionMembers.actor_id == entity.id)
                            & (FactionMembers.faction_id == related_entity.id)
                        )
                        .first()
                    )

                    if membership:
                        return {
                            # New structured fields
                            "role": membership.role or "",
                            "rank": membership.rank or 1,
                            "membership_status": membership.membership_status or "",
                            "responsibilities": membership.responsibilities or "",
                            "loyalty": membership.loyalty or 7,
                            "join_date": membership.join_date or "",
                            # Legacy fields (for backward compatibility)
                            "actor_role": membership.actor_role or "",
                            "relative_power": membership.relative_power or 1,
                        }

                # Add more relationship types as needed
                return {}

        except Exception as e:
            print(f"Error getting relationship data for {relationship_name}: {e}")
            return {}

    def search_entities(self, table_name: str, search_term: str) -> List[Any]:
        """Search entities by text content"""
        table_class = self.table_classes.get(table_name)
        if not table_class:
            return []

        try:
            with Session(self.model.engine) as session:
                query = session.query(table_class).filter_by(setting_id=self.setting_id)

                # Add search filters based on common text fields
                if hasattr(table_class, "name"):
                    query = query.filter(table_class.name.ilike(f"%{search_term}%"))
                elif hasattr(table_class, "first_name"):
                    query = query.filter(
                        table_class.first_name.ilike(f"%{search_term}%")
                        | table_class.last_name.ilike(f"%{search_term}%")
                    )
                elif hasattr(table_class, "title"):
                    query = query.filter(table_class.title.ilike(f"%{search_term}%"))

                # Also search in description if available
                if hasattr(table_class, "description"):
                    query = query.filter(
                        table_class.description.ilike(f"%{search_term}%")
                    )

                return query.all()
        except Exception as e:
            print(f"Error searching entities in {table_name}: {e}")
            return []

    def get_location_details(self, location_entity: Any) -> Dict[str, Any]:
        """Get additional location details (dungeon, city, etc.) for a location"""
        details = {}

        try:
            with Session(self.model.engine) as session:
                location = session.merge(location_entity)

                # Get dungeon details if exists
                if hasattr(location, "is_dungeon") and location.is_dungeon:
                    dungeon = (
                        session.query(LocationDungeon)
                        .filter_by(location_id=location.id)
                        .first()
                    )
                    if dungeon:
                        details.update(
                            {
                                "dangers": dungeon.dangers,
                                "traps": dungeon.traps,
                                "secrets": dungeon.secrets,
                            }
                        )

                # Get city details if exists
                if hasattr(location, "is_city") and location.is_city:
                    city = (
                        session.query(LocationCity)
                        .filter_by(location_id=location.id)
                        .first()
                    )
                    if city:
                        details.update(
                            {
                                "government": city.government,
                            }
                        )

                return details

        except Exception as e:
            print(f"Error getting location details: {e}")
            return {}

    def save_location_details(
        self, location_entity: Any, details_data: Dict[str, Any]
    ) -> bool:
        """Save additional location details based on location type flags"""
        try:
            with Session(self.model.engine) as session:
                location = session.merge(location_entity)

                # Handle dungeon details
                if hasattr(location, "is_dungeon") and location.is_dungeon:
                    dungeon = (
                        session.query(LocationDungeon)
                        .filter_by(location_id=location.id)
                        .first()
                    )
                    if not dungeon:
                        dungeon = LocationDungeon(
                            location_id=location.id, setting_id=self.setting_id
                        )
                        session.add(dungeon)

                    # Update dungeon fields
                    dungeon.dangers = details_data.get("dangers", "")
                    dungeon.traps = details_data.get("traps", "")
                    dungeon.secrets = details_data.get("secrets", "")

                # Handle city details
                if hasattr(location, "is_city") and location.is_city:
                    city = (
                        session.query(LocationCity)
                        .filter_by(location_id=location.id)
                        .first()
                    )
                    if not city:
                        city = LocationCity(
                            location_id=location.id, setting_id=self.setting_id
                        )
                        session.add(city)

                    # Update city fields
                    city.government = details_data.get("government", "")

                session.commit()
                return True

        except Exception as e:
            print(f"Error saving location details: {e}")
            return False
