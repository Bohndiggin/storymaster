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
        }

    def get_entities(self, table_name: str) -> List[Any]:
        """Get all entities for a given table type"""
        table_class = self.table_classes.get(table_name)
        if not table_class:
            return []

        try:
            with Session(self.model.engine) as session:
                return (
                    session.query(table_class)
                    .filter_by(setting_id=self.setting_id)
                    .all()
                )
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
                return (
                    session.query(table_class)
                    .filter_by(id=entity_id, setting_id=self.setting_id)
                    .first()
                )
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
                    from storymaster.model.database.schema.base import ActorAOnBRelations
                    relations = session.query(ActorAOnBRelations).filter(
                        (ActorAOnBRelations.actor_a_id == entity.id) |
                        (ActorAOnBRelations.actor_b_id == entity.id)
                    ).all()
                    
                    related_entities = []
                    for rel in relations:
                        if rel.actor_a_id == entity.id:
                            related_entities.append(rel.actor_b)
                        else:
                            related_entities.append(rel.actor_a)
                    return related_entities
                
                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers
                    if hasattr(entity, 'members'):  # Faction entity
                        return [member.actor for member in entity.members]
                    elif hasattr(entity, 'faction_memberships'):  # Actor entity
                        return [membership.faction for membership in entity.faction_memberships]
                
                elif relationship_name == "residents":
                    from storymaster.model.database.schema.base import Resident
                    if hasattr(entity, 'residents'):  # Location entity
                        return [resident.actor for resident in entity.residents]
                    elif hasattr(entity, 'residences'):  # Actor entity
                        return [residence.location for residence in entity.residences]
                
                # Add more relationship types as needed
                return []
                
        except Exception as e:
            print(f"Error getting relationship entities for {relationship_name}: {e}")
            return []

    def add_relationship(
        self, entity: Any, relationship_name: str, related_entity: Any, relationship_data: dict = None
    ) -> bool:
        """Add a relationship between entities"""
        try:
            with Session(self.model.engine) as session:
                # Re-attach entities to session
                entity = session.merge(entity)
                related_entity = session.merge(related_entity)
                
                # Create relationship based on type
                if relationship_name == "actor_a_on_b_relations":
                    from storymaster.model.database.schema.base import ActorAOnBRelations
                    
                    # Check if relationship already exists
                    existing = session.query(ActorAOnBRelations).filter(
                        ((ActorAOnBRelations.actor_a_id == entity.id) & 
                         (ActorAOnBRelations.actor_b_id == related_entity.id)) |
                        ((ActorAOnBRelations.actor_a_id == related_entity.id) & 
                         (ActorAOnBRelations.actor_b_id == entity.id))
                    ).first()
                    
                    if existing:
                        return False  # Relationship already exists
                    
                    # Create new relationship
                    new_relation = ActorAOnBRelations(
                        actor_a_id=entity.id,
                        actor_b_id=related_entity.id,
                        setting_id=self.setting_id,
                        overall=relationship_data.get('description', '') if relationship_data else '',
                        power_dynamic=relationship_data.get('relationship_type', '') if relationship_data else ''
                    )
                    session.add(new_relation)
                
                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers
                    
                    # Check if membership already exists
                    existing = session.query(FactionMembers).filter(
                        (FactionMembers.actor_id == entity.id) &
                        (FactionMembers.faction_id == related_entity.id)
                    ).first()
                    
                    if existing:
                        return False  # Membership already exists
                    
                    # Create new membership
                    new_membership = FactionMembers(
                        actor_id=entity.id,
                        faction_id=related_entity.id,
                        setting_id=self.setting_id,
                        actor_role=relationship_data.get('role', '') if relationship_data else '',
                        relative_power=relationship_data.get('rank', 1) if relationship_data else 1
                    )
                    session.add(new_membership)
                
                elif relationship_name == "residents":
                    from storymaster.model.database.schema.base import Resident
                    
                    # Check if residency already exists
                    existing = session.query(Resident).filter(
                        (Resident.actor_id == entity.id) &
                        (Resident.location_id == related_entity.id)
                    ).first()
                    
                    if existing:
                        return False  # Residency already exists
                    
                    # Create new residency
                    new_residency = Resident(
                        actor_id=entity.id,
                        location_id=related_entity.id,
                        setting_id=self.setting_id
                    )
                    session.add(new_residency)
                
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
                    from storymaster.model.database.schema.base import ActorAOnBRelations
                    
                    relation = session.query(ActorAOnBRelations).filter(
                        ((ActorAOnBRelations.actor_a_id == entity.id) & 
                         (ActorAOnBRelations.actor_b_id == related_entity.id)) |
                        ((ActorAOnBRelations.actor_a_id == related_entity.id) & 
                         (ActorAOnBRelations.actor_b_id == entity.id))
                    ).first()
                    
                    if relation:
                        session.delete(relation)
                
                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers
                    
                    membership = session.query(FactionMembers).filter(
                        (FactionMembers.actor_id == entity.id) &
                        (FactionMembers.faction_id == related_entity.id)
                    ).first()
                    
                    if membership:
                        session.delete(membership)
                
                elif relationship_name == "residents":
                    from storymaster.model.database.schema.base import Resident
                    
                    residency = session.query(Resident).filter(
                        (Resident.actor_id == entity.id) &
                        (Resident.location_id == related_entity.id)
                    ).first()
                    
                    if residency:
                        session.delete(residency)
                
                # Add more relationship types as needed
                
                session.commit()
                return True
                
        except Exception as e:
            print(f"Error removing relationship {relationship_name}: {e}")
            return False

    def update_relationship(
        self, entity: Any, relationship_name: str, related_entity: Any, relationship_data: dict
    ) -> bool:
        """Update an existing relationship with new data"""
        try:
            with Session(self.model.engine) as session:
                # Update relationship based on type
                if relationship_name == "actor_a_on_b_relations":
                    from storymaster.model.database.schema.base import ActorAOnBRelations
                    
                    relation = session.query(ActorAOnBRelations).filter(
                        ((ActorAOnBRelations.actor_a_id == entity.id) & 
                         (ActorAOnBRelations.actor_b_id == related_entity.id)) |
                        ((ActorAOnBRelations.actor_a_id == related_entity.id) & 
                         (ActorAOnBRelations.actor_b_id == entity.id))
                    ).first()
                    
                    if relation:
                        # Map comprehensive relationship data to available database fields
                        # overall: store the main description and key details
                        description = relationship_data.get('description', '')
                        notes = relationship_data.get('notes', '')
                        timeline = relationship_data.get('timeline', '')
                        how_met = relationship_data.get('how_met', '')
                        shared_history = relationship_data.get('shared_history', '')
                        
                        # Combine all descriptive text into the overall field
                        overall_parts = []
                        if description:
                            overall_parts.append(f"Description: {description}")
                        if how_met:
                            overall_parts.append(f"How they met: {how_met}")
                        if shared_history:
                            overall_parts.append(f"Shared history: {shared_history}")
                        if timeline:
                            overall_parts.append(f"Timeline: {timeline}")
                        if notes:
                            overall_parts.append(f"Notes: {notes}")
                        
                        relation.overall = " | ".join(overall_parts) if overall_parts else relation.overall
                        
                        # power_dynamic: store relationship type and trust info
                        rel_type = relationship_data.get('relationship_type', '')
                        trust_level = relationship_data.get('trust_level', '')
                        is_mutual = relationship_data.get('is_mutual', True)
                        
                        power_parts = []
                        if rel_type:
                            power_parts.append(f"Type: {rel_type}")
                        if trust_level:
                            power_parts.append(f"Trust: {trust_level}/10")
                        if not is_mutual:
                            power_parts.append("One-sided")
                        
                        relation.power_dynamic = " | ".join(power_parts) if power_parts else relation.power_dynamic
                        
                        # economically: store current status and strength
                        current_status = relationship_data.get('current_status', '')
                        status = relationship_data.get('status', '')
                        strength = relationship_data.get('strength', '')
                        
                        econ_parts = []
                        if status:
                            econ_parts.append(f"Status: {status}")
                        if strength:
                            econ_parts.append(f"Strength: {strength}/10")
                        if current_status:
                            econ_parts.append(f"Current: {current_status}")
                        
                        relation.economically = " | ".join(econ_parts) if econ_parts else relation.economically
                
                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers
                    
                    membership = session.query(FactionMembers).filter(
                        (FactionMembers.actor_id == entity.id) &
                        (FactionMembers.faction_id == related_entity.id)
                    ).first()
                    
                    if membership:
                        # Map membership dialog data to database fields
                        role = relationship_data.get('role', '')
                        membership_status = relationship_data.get('membership_status', '')
                        responsibilities = relationship_data.get('responsibilities', '')
                        
                        # Combine role information into actor_role field
                        role_parts = []
                        if role:
                            role_parts.append(role)
                        if membership_status:
                            role_parts.append(f"({membership_status})")
                        if responsibilities:
                            role_parts.append(f"Duties: {responsibilities}")
                        
                        membership.actor_role = " | ".join(role_parts) if role_parts else membership.actor_role
                        
                        # Update rank/power level
                        rank = relationship_data.get('rank')
                        if rank is not None:
                            membership.relative_power = rank
                
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
                    from storymaster.model.database.schema.base import ActorAOnBRelations
                    
                    relation = session.query(ActorAOnBRelations).filter(
                        ((ActorAOnBRelations.actor_a_id == entity.id) & 
                         (ActorAOnBRelations.actor_b_id == related_entity.id)) |
                        ((ActorAOnBRelations.actor_a_id == related_entity.id) & 
                         (ActorAOnBRelations.actor_b_id == entity.id))
                    ).first()
                    
                    if relation:
                        return {
                            'overall': relation.overall or '',
                            'power_dynamic': relation.power_dynamic or '',
                            'economically': relation.economically or ''
                        }
                
                elif relationship_name == "faction_members":
                    from storymaster.model.database.schema.base import FactionMembers
                    
                    membership = session.query(FactionMembers).filter(
                        (FactionMembers.actor_id == entity.id) &
                        (FactionMembers.faction_id == related_entity.id)
                    ).first()
                    
                    if membership:
                        return {
                            'actor_role': membership.actor_role or '',
                            'relative_power': membership.relative_power or 1
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
