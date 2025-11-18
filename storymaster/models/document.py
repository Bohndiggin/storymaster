"""
Document model and file handling for .storyweaver format.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class StoryDocument:
    """Represents a StoryWeaver document (.storyweaver bundle)."""

    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.content = ""
        self.metadata = {
            "storymaster_db": "",
            "last_sync": datetime.now().isoformat(),
            "entity_map": {}
        }
        self._is_modified = False

        if path and os.path.exists(path):
            self.load()

    @property
    def is_modified(self) -> bool:
        """Check if document has unsaved changes."""
        return self._is_modified

    @property
    def document_path(self) -> Optional[Path]:
        """Get the document path as a Path object."""
        return Path(self.path) if self.path else None

    @property
    def markdown_path(self) -> Optional[Path]:
        """Get the path to the markdown file."""
        if not self.path:
            return None
        return Path(self.path) / "document.md"

    @property
    def metadata_path(self) -> Optional[Path]:
        """Get the path to the metadata file."""
        if not self.path:
            return None
        return Path(self.path) / "metadata.json"

    @property
    def cache_db_path(self) -> Optional[Path]:
        """Get the path to the cache database."""
        if not self.path:
            return None
        return Path(self.path) / "cache.db"

    def set_content(self, content: str) -> None:
        """Set the document content and mark as modified."""
        if self.content != content:
            self.content = content
            self._is_modified = True

    def update_entity(self, entity_id: str, name: str, entity_type: str) -> None:
        """Update or add an entity to the entity map."""
        # Preserve existing aliases if entity already exists
        existing_aliases = []
        if entity_id in self.metadata["entity_map"]:
            existing_aliases = self.metadata["entity_map"][entity_id].get("aliases", [])

        self.metadata["entity_map"][entity_id] = {
            "name": name,
            "type": entity_type,
            "last_seen": datetime.now().isoformat(),
            "aliases": existing_aliases
        }
        self._is_modified = True

    def get_entity_name(self, entity_id: str) -> Optional[str]:
        """Get the cached name for an entity."""
        entity = self.metadata["entity_map"].get(entity_id)
        return entity["name"] if entity else None

    def add_alias(self, entity_id: str, alias: str) -> bool:
        """
        Add an alias for an entity.

        Args:
            entity_id: The entity ID
            alias: The alias to add

        Returns:
            True if added successfully, False if entity not found or alias already exists
        """
        if entity_id not in self.metadata["entity_map"]:
            return False

        entity = self.metadata["entity_map"][entity_id]
        if "aliases" not in entity:
            entity["aliases"] = []

        # Don't add duplicates
        if alias in entity["aliases"]:
            return False

        # Don't add the canonical name as an alias
        if alias == entity["name"]:
            return False

        entity["aliases"].append(alias)
        self._is_modified = True
        return True

    def remove_alias(self, entity_id: str, alias: str) -> bool:
        """
        Remove an alias from an entity.

        Args:
            entity_id: The entity ID
            alias: The alias to remove

        Returns:
            True if removed successfully, False if not found
        """
        if entity_id not in self.metadata["entity_map"]:
            return False

        entity = self.metadata["entity_map"][entity_id]
        if "aliases" not in entity or alias not in entity["aliases"]:
            return False

        entity["aliases"].remove(alias)
        self._is_modified = True
        return True

    def get_aliases(self, entity_id: str) -> list:
        """
        Get all aliases for an entity.

        Args:
            entity_id: The entity ID

        Returns:
            List of aliases (empty if none or entity not found)
        """
        if entity_id not in self.metadata["entity_map"]:
            return []

        entity = self.metadata["entity_map"][entity_id]
        return entity.get("aliases", [])

    def get_all_names_for_entity(self, entity_id: str) -> list:
        """
        Get all names (canonical + aliases) for an entity.

        Args:
            entity_id: The entity ID

        Returns:
            List containing canonical name and all aliases
        """
        if entity_id not in self.metadata["entity_map"]:
            return []

        entity = self.metadata["entity_map"][entity_id]
        names = [entity["name"]]
        names.extend(entity.get("aliases", []))
        return names

    def set_storymaster_db(self, db_path: str) -> None:
        """Set the path to the Storymaster database."""
        self.metadata["storymaster_db"] = db_path
        self._is_modified = True

    def create_new(self, path: str) -> None:
        """Create a new document at the specified path."""
        self.path = path
        self.content = ""
        self.metadata = {
            "storymaster_db": "",
            "last_sync": datetime.now().isoformat(),
            "entity_map": {}
        }
        self._is_modified = True
        self.save()

    def save(self) -> bool:
        """Save the document to disk."""
        if not self.path:
            return False

        try:
            # Create directory if it doesn't exist
            doc_dir = Path(self.path)
            doc_dir.mkdir(parents=True, exist_ok=True)

            # Save markdown content
            with open(self.markdown_path, 'w', encoding='utf-8') as f:
                f.write(self.content)

            # Update last sync time
            self.metadata["last_sync"] = datetime.now().isoformat()

            # Save metadata
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)

            self._is_modified = False
            return True

        except Exception as e:
            print(f"Error saving document: {e}")
            return False

    def load(self) -> bool:
        """Load the document from disk."""
        if not self.path or not os.path.exists(self.path):
            return False

        try:
            # Load markdown content
            if self.markdown_path.exists():
                with open(self.markdown_path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
            else:
                self.content = ""

            # Load metadata
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {
                    "storymaster_db": "",
                    "last_sync": datetime.now().isoformat(),
                    "entity_map": {}
                }

            self._is_modified = False
            return True

        except Exception as e:
            print(f"Error loading document: {e}")
            return False

    def get_all_entity_ids(self) -> list:
        """Extract all entity IDs from the document content."""
        import re
        pattern = r'\[\[([^\]|]+)\|([^\]]+)\]\]'
        matches = re.findall(pattern, self.content)
        return [entity_id for _, entity_id in matches]

    def get_entity_references(self) -> Dict[str, Dict[str, Any]]:
        """Get all entity references with their display names from content."""
        import re
        pattern = r'\[\[([^\]|]+)\|([^\]]+)\]\]'
        matches = re.findall(pattern, self.content)

        references = {}
        for display_name, entity_id in matches:
            if entity_id not in references:
                # Check if we have cached info
                cached = self.metadata["entity_map"].get(entity_id, {})
                references[entity_id] = {
                    "display_name": display_name,
                    "type": cached.get("type", "unknown"),
                    "cached_name": cached.get("name", display_name)
                }

        return references
