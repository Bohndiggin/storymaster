"""
Document model and file handling for .storyweaver format.
"""
import json
import os
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class StoryDocument:
    """Represents a StoryWeaver document (.storyweaver ZIP file)."""

    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.content = ""
        self.metadata = {
            "storymaster_db": "",
            "last_sync": datetime.now().isoformat(),
            "entity_map": {}
        }
        self._is_modified = False

        if path and os.path.isfile(path):
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
        """
        [Deprecated] Markdown is now stored inside the ZIP file.
        Returns None as there is no direct file path.
        """
        return None

    @property
    def metadata_path(self) -> Optional[Path]:
        """
        [Deprecated] Metadata is now stored inside the ZIP file.
        Returns None as there is no direct file path.
        """
        return None

    @property
    def cache_db_path(self) -> Optional[Path]:
        """
        [Deprecated] Cache DB would be stored inside the ZIP file.
        Returns None as there is no direct file path.
        """
        return None

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
        """Save the document to disk as a ZIP file."""
        if not self.path:
            return False

        try:
            # Update last sync time
            self.metadata["last_sync"] = datetime.now().isoformat()

            # Create a temporary file for atomic save
            temp_fd, temp_path = tempfile.mkstemp(suffix='.storyweaver')
            os.close(temp_fd)  # Close the file descriptor

            try:
                # Write to ZIP file
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    # Write markdown content
                    zf.writestr('document.md', self.content.encode('utf-8'))

                    # Write metadata as JSON
                    metadata_json = json.dumps(self.metadata, indent=2)
                    zf.writestr('metadata.json', metadata_json.encode('utf-8'))

                # Atomic move: replace old file with new one
                import shutil
                shutil.move(temp_path, self.path)

                self._is_modified = False
                return True

            except Exception:
                # Clean up temp file if something went wrong
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise

        except Exception as e:
            print(f"Error saving document: {e}")
            return False

    def load(self) -> bool:
        """Load the document from disk (ZIP file)."""
        if not self.path or not os.path.isfile(self.path):
            return False

        try:
            with zipfile.ZipFile(self.path, 'r') as zf:
                # Load markdown content
                try:
                    content_bytes = zf.read('document.md')
                    self.content = content_bytes.decode('utf-8')
                except KeyError:
                    self.content = ""

                # Load metadata
                try:
                    metadata_bytes = zf.read('metadata.json')
                    self.metadata = json.loads(metadata_bytes.decode('utf-8'))
                except KeyError:
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
