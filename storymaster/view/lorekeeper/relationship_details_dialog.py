"""Relationship details dialog for viewing and editing relationship specifics"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, 
    QSpinBox, QSlider, QGroupBox, QCheckBox, QDateEdit
)
from PyQt6.QtGui import QFont
from datetime import datetime

from storymaster.model.lorekeeper.entity_mappings import get_entity_mapping


class RelationshipDetailsDialog(QDialog):
    """Dialog for viewing and editing relationship details between entities"""
    
    def __init__(self, relationship_type: str, source_entity, target_entity, model_adapter, parent=None):
        super().__init__(parent)
        self.relationship_type = relationship_type
        self.source_entity = source_entity
        self.target_entity = target_entity
        self.model_adapter = model_adapter
        self.relationship_data = {}
        self.setup_ui()
        self.load_relationship_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle(f"Relationship Details: {self.get_relationship_title()}")
        self.setModal(True)
        self.resize(600, 700)
        
        layout = QVBoxLayout()
        
        # Header with relationship overview
        header = self.create_header()
        layout.addWidget(header)
        
        # Tabbed interface for different aspects of the relationship
        self.tab_widget = QTabWidget()
        
        # Basic relationship tab
        basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(basic_tab, "Basic Info")
        
        # Relationship-specific tabs based on type
        if self.relationship_type == "actor_a_on_b_relations":
            self.tab_widget.addTab(self.create_character_relationship_tab(), "Character Dynamics")
        elif self.relationship_type == "faction_members":
            self.tab_widget.addTab(self.create_membership_tab(), "Membership Details")
        elif self.relationship_type == "location_to_faction":
            self.tab_widget.addTab(self.create_territory_tab(), "Territory Control")
        elif self.relationship_type.startswith("history_"):
            self.tab_widget.addTab(self.create_historical_involvement_tab(), "Historical Context")
        
        # Timeline/History tab
        timeline_tab = self.create_timeline_tab()
        self.tab_widget.addTab(timeline_tab, "Timeline")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_relationship)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_header(self) -> QGroupBox:
        """Create the header section with relationship overview"""
        header = QGroupBox("Relationship Overview")
        layout = QVBoxLayout()
        
        # Relationship title
        title = QLabel(self.get_relationship_title())
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Entity details
        source_name = self.get_entity_display_name(self.source_entity)
        target_name = self.get_entity_display_name(self.target_entity)
        
        details = QLabel(f"{source_name} ↔ {target_name}")
        details.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(details)
        
        # Relationship type explanation
        explanation = self.get_relationship_explanation()
        if explanation:
            explanation_label = QLabel(explanation)
            explanation_label.setWordWrap(True)
            explanation_label.setStyleSheet("color: #888; font-style: italic; margin: 8px 0;")
            layout.addWidget(explanation_label)
        
        header.setLayout(layout)
        return header
    
    def create_basic_tab(self) -> QGroupBox:
        """Create the basic relationship information tab"""
        tab = QGroupBox()
        layout = QFormLayout()
        
        # Relationship status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "Historical", "Potential", "Complicated"])
        layout.addRow("Status:", self.status_combo)
        
        # Relationship strength/intensity
        self.strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.strength_slider.setRange(1, 10)
        self.strength_slider.setValue(5)
        self.strength_label = QLabel("5")
        self.strength_slider.valueChanged.connect(lambda v: self.strength_label.setText(str(v)))
        
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(self.strength_slider)
        strength_layout.addWidget(self.strength_label)
        layout.addRow("Strength (1-10):", strength_layout)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Describe this relationship...")
        layout.addRow("Description:", self.description_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes...")
        layout.addRow("Notes:", self.notes_edit)
        
        # Public/Private
        self.is_public = QCheckBox("This relationship is public knowledge")
        self.is_public.setChecked(True)
        layout.addRow("Visibility:", self.is_public)
        
        tab.setLayout(layout)
        return tab
    
    def create_character_relationship_tab(self) -> QGroupBox:
        """Create tab for character-to-character relationships"""
        tab = QGroupBox()
        layout = QFormLayout()
        
        # Relationship type
        self.char_relationship_type = QComboBox()
        self.char_relationship_type.addItems([
            "Friend", "Enemy", "Family", "Romantic", "Professional", 
            "Mentor/Student", "Rival", "Ally", "Neutral", "Complicated"
        ])
        layout.addRow("Relationship Type:", self.char_relationship_type)
        
        # Mutual/One-sided
        self.is_mutual = QCheckBox("This relationship is mutual")
        self.is_mutual.setChecked(True)
        layout.addRow("Nature:", self.is_mutual)
        
        # Trust level
        self.trust_slider = QSlider(Qt.Orientation.Horizontal)
        self.trust_slider.setRange(1, 10)
        self.trust_slider.setValue(5)
        self.trust_label = QLabel("5")
        self.trust_slider.valueChanged.connect(lambda v: self.trust_label.setText(str(v)))
        
        trust_layout = QHBoxLayout()
        trust_layout.addWidget(self.trust_slider)
        trust_layout.addWidget(self.trust_label)
        layout.addRow("Trust Level:", trust_layout)
        
        # How they met
        self.how_met_edit = QTextEdit()
        self.how_met_edit.setMaximumHeight(80)
        self.how_met_edit.setPlaceholderText("How did they first meet?")
        layout.addRow("First Meeting:", self.how_met_edit)
        
        # Shared history
        self.shared_history_edit = QTextEdit()
        self.shared_history_edit.setMaximumHeight(80)
        self.shared_history_edit.setPlaceholderText("What experiences have they shared?")
        layout.addRow("Shared History:", self.shared_history_edit)
        
        # Current status
        self.current_status_edit = QLineEdit()
        self.current_status_edit.setPlaceholderText("Current state of their relationship")
        layout.addRow("Current Status:", self.current_status_edit)
        
        tab.setLayout(layout)
        return tab
    
    def create_membership_tab(self) -> QGroupBox:
        """Create tab for faction membership details"""
        tab = QGroupBox()
        layout = QFormLayout()
        
        # Role in organization
        self.role_edit = QLineEdit()
        self.role_edit.setPlaceholderText("Member's role or title")
        layout.addRow("Role/Title:", self.role_edit)
        
        # Rank/Level
        self.rank_spin = QSpinBox()
        self.rank_spin.setRange(1, 100)
        self.rank_spin.setValue(1)
        layout.addRow("Rank/Level:", self.rank_spin)
        
        # Join date
        self.join_date = QDateEdit()
        self.join_date.setDate(datetime.now().date())
        self.join_date.setCalendarPopup(True)
        layout.addRow("Join Date:", self.join_date)
        
        # Loyalty level
        self.loyalty_slider = QSlider(Qt.Orientation.Horizontal)
        self.loyalty_slider.setRange(1, 10)
        self.loyalty_slider.setValue(7)
        self.loyalty_label = QLabel("7")
        self.loyalty_slider.valueChanged.connect(lambda v: self.loyalty_label.setText(str(v)))
        
        loyalty_layout = QHBoxLayout()
        loyalty_layout.addWidget(self.loyalty_slider)
        loyalty_layout.addWidget(self.loyalty_label)
        layout.addRow("Loyalty:", loyalty_layout)
        
        # Responsibilities
        self.responsibilities_edit = QTextEdit()
        self.responsibilities_edit.setMaximumHeight(80)
        self.responsibilities_edit.setPlaceholderText("What are their responsibilities?")
        layout.addRow("Responsibilities:", self.responsibilities_edit)
        
        # Status
        self.membership_status = QComboBox()
        self.membership_status.addItems([
            "Active Member", "Inactive", "On Leave", "Probation", 
            "Leadership", "Founder", "Honorary", "Former Member"
        ])
        layout.addRow("Membership Status:", self.membership_status)
        
        tab.setLayout(layout)
        return tab
    
    def create_territory_tab(self) -> QGroupBox:
        """Create tab for location-faction territory control"""
        tab = QGroupBox()
        layout = QFormLayout()
        
        # Control type
        self.control_type = QComboBox()
        self.control_type.addItems([
            "Full Control", "Partial Control", "Influence", "Presence", 
            "Claims", "Disputed", "Historical", "Temporary"
        ])
        layout.addRow("Control Type:", self.control_type)
        
        # Control strength
        self.control_strength = QSlider(Qt.Orientation.Horizontal)
        self.control_strength.setRange(1, 10)
        self.control_strength.setValue(5)
        self.control_strength_label = QLabel("5")
        self.control_strength.valueChanged.connect(lambda v: self.control_strength_label.setText(str(v)))
        
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.control_strength)
        control_layout.addWidget(self.control_strength_label)
        layout.addRow("Control Strength:", control_layout)
        
        # How control was established
        self.control_method_edit = QTextEdit()
        self.control_method_edit.setMaximumHeight(80)
        self.control_method_edit.setPlaceholderText("How did they gain control?")
        layout.addRow("Control Method:", self.control_method_edit)
        
        # Resources/Benefits
        self.resources_edit = QTextEdit()
        self.resources_edit.setMaximumHeight(80)
        self.resources_edit.setPlaceholderText("What resources or benefits does this provide?")
        layout.addRow("Resources/Benefits:", self.resources_edit)
        
        # Challenges
        self.challenges_edit = QTextEdit()
        self.challenges_edit.setMaximumHeight(80)
        self.challenges_edit.setPlaceholderText("What challenges do they face here?")
        layout.addRow("Challenges:", self.challenges_edit)
        
        tab.setLayout(layout)
        return tab
    
    def create_historical_involvement_tab(self) -> QGroupBox:
        """Create tab for historical event involvement"""
        tab = QGroupBox()
        layout = QFormLayout()
        
        # Role in event
        self.event_role_edit = QLineEdit()
        self.event_role_edit.setPlaceholderText("What role did they play?")
        layout.addRow("Role in Event:", self.event_role_edit)
        
        # Level of involvement
        self.involvement_level = QComboBox()
        self.involvement_level.addItems([
            "Central Figure", "Major Participant", "Minor Participant", 
            "Witness", "Affected Party", "Catalyst", "Victim", "Hero"
        ])
        layout.addRow("Involvement Level:", self.involvement_level)
        
        # Impact on entity
        self.impact_edit = QTextEdit()
        self.impact_edit.setMaximumHeight(80)
        self.impact_edit.setPlaceholderText("How did this event impact them?")
        layout.addRow("Impact:", self.impact_edit)
        
        # Their perspective
        self.perspective_edit = QTextEdit()
        self.perspective_edit.setMaximumHeight(80)
        self.perspective_edit.setPlaceholderText("How do they view this event?")
        layout.addRow("Their Perspective:", self.perspective_edit)
        
        # Consequences
        self.consequences_edit = QTextEdit()
        self.consequences_edit.setMaximumHeight(80)
        self.consequences_edit.setPlaceholderText("What were the consequences for them?")
        layout.addRow("Consequences:", self.consequences_edit)
        
        tab.setLayout(layout)
        return tab
    
    def create_timeline_tab(self) -> QGroupBox:
        """Create tab for relationship timeline"""
        tab = QGroupBox()
        layout = QVBoxLayout()
        
        # Timeline entries
        timeline_header = QLabel("Relationship Timeline")
        font = QFont()
        font.setBold(True)
        timeline_header.setFont(font)
        layout.addWidget(timeline_header)
        
        # Timeline text area
        self.timeline_edit = QTextEdit()
        self.timeline_edit.setPlaceholderText(
            "Record key moments in this relationship:\n\n"
            "Year 1023: First met at the tavern\n"
            "Year 1024: Became allies during the siege\n"
            "Year 1025: Had a falling out over treasure\n"
            "Present: Cautious cooperation"
        )
        layout.addWidget(self.timeline_edit)
        
        tab.setLayout(layout)
        return tab
    
    def get_relationship_title(self) -> str:
        """Get a user-friendly title for this relationship"""
        relationship_titles = {
            "actor_a_on_b_relations": "Character Relationship",
            "faction_members": "Organization Membership",
            "residents": "Residence",
            "actor_to_skills": "Skill Knowledge",
            "actor_to_race": "Heritage",
            "actor_to_class": "Profession",
            "object_to_owner": "Item Ownership",
            "location_to_faction": "Territory Control",
            "history_actor": "Historical Involvement",
            "history_location": "Historical Location",
            "history_faction": "Historical Organization",
            "history_object": "Historical Artifact",
        }
        
        return relationship_titles.get(self.relationship_type, "Relationship")
    
    def get_relationship_explanation(self) -> str:
        """Get an explanation of what this relationship represents"""
        explanations = {
            "actor_a_on_b_relations": "The dynamic between these two characters - how they know each other, what they think of each other, and their shared history.",
            "faction_members": "Details about this character's membership in the organization, including their role, rank, and status.",
            "residents": "Information about where this character lives and their connection to this location.",
            "location_to_faction": "How this organization controls, influences, or has presence in this location.",
            "history_actor": "This character's involvement in the historical event and how it affected them.",
            "object_to_owner": "Details about how this character owns or possesses this item.",
        }
        
        return explanations.get(self.relationship_type, "")
    
    def get_entity_display_name(self, entity) -> str:
        """Get display name for an entity"""
        if hasattr(entity, "name") and entity.name:
            return entity.name
        elif hasattr(entity, "first_name") and entity.first_name:
            name_parts = [entity.first_name]
            if hasattr(entity, "last_name") and entity.last_name:
                name_parts.append(entity.last_name)
            return " ".join(name_parts)
        elif hasattr(entity, "title") and entity.title:
            return entity.title
        else:
            return f"ID: {getattr(entity, 'id', 'Unknown')}"
    
    def load_relationship_data(self):
        """Load existing relationship data if available"""
        try:
            # Get existing relationship data from the database
            existing_data = self.model_adapter.get_relationship_data(
                self.source_entity, 
                self.relationship_type, 
                self.target_entity
            )
            
            if existing_data:
                # Parse and populate the form fields with existing data
                if self.relationship_type == "actor_a_on_b_relations":
                    self.parse_actor_relationship_data(existing_data)
                elif self.relationship_type == "faction_members":
                    self.parse_membership_data(existing_data)
                    
        except Exception as e:
            print(f"Error loading relationship data: {e}")
            # Continue with default values if loading fails
    
    def parse_actor_relationship_data(self, data):
        """Parse actor relationship data from database format"""
        # Use new structured fields directly
        self.description_edit.setPlainText(data.get('description', ''))
        self.notes_edit.setPlainText(data.get('notes', ''))
        self.timeline_edit.setPlainText(data.get('timeline', ''))
        self.how_met_edit.setPlainText(data.get('how_met', ''))
        self.shared_history_edit.setPlainText(data.get('shared_history', ''))
        self.current_status_edit.setText(data.get('current_status', ''))
        
        # Set relationship type
        rel_type = data.get('relationship_type', '')
        if rel_type:
            index = self.char_relationship_type.findText(rel_type)
            if index >= 0:
                self.char_relationship_type.setCurrentIndex(index)
        
        # Set status
        status = data.get('status', '')
        if status:
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        # Set sliders
        self.strength_slider.setValue(data.get('strength', 5))
        self.trust_slider.setValue(data.get('trust_level', 5))
        
        # Set checkboxes
        self.is_mutual.setChecked(data.get('is_mutual', True))
        self.is_public.setChecked(data.get('is_public', True))
    
    def parse_membership_data(self, data):
        """Parse faction membership data from database format"""
        # Use new structured fields directly
        self.role_edit.setText(data.get('role', ''))
        self.rank_spin.setValue(data.get('rank', 1))
        self.responsibilities_edit.setPlainText(data.get('responsibilities', ''))
        self.loyalty_slider.setValue(data.get('loyalty', 7))
        
        # Set membership status
        membership_status = data.get('membership_status', '')
        if membership_status:
            index = self.membership_status.findText(membership_status)
            if index >= 0:
                self.membership_status.setCurrentIndex(index)
                
        # Set join date if available
        join_date = data.get('join_date', '')
        if join_date:
            # Parse join date string and set the date widget
            # For now, just store it as string format
            pass
    
    def save_relationship(self):
        """Save the relationship data"""
        # Collect all the form data
        self.relationship_data = {
            "status": self.status_combo.currentText(),
            "strength": self.strength_slider.value(),
            "description": self.description_edit.toPlainText(),
            "notes": self.notes_edit.toPlainText(),
            "is_public": self.is_public.isChecked(),
            "timeline": self.timeline_edit.toPlainText(),
        }
        
        # Add relationship-specific data
        if self.relationship_type == "actor_a_on_b_relations":
            self.relationship_data.update({
                "relationship_type": self.char_relationship_type.currentText(),
                "is_mutual": self.is_mutual.isChecked(),
                "trust_level": self.trust_slider.value(),
                "how_met": self.how_met_edit.toPlainText(),
                "shared_history": self.shared_history_edit.toPlainText(),
                "current_status": self.current_status_edit.text(),
            })
        elif self.relationship_type == "faction_members":
            self.relationship_data.update({
                "role": self.role_edit.text(),
                "rank": self.rank_spin.value(),
                "join_date": self.join_date.date().toString(),
                "loyalty": self.loyalty_slider.value(),
                "responsibilities": self.responsibilities_edit.toPlainText(),
                "membership_status": self.membership_status.currentText(),
            })
        
        # Actually save to the database
        from PyQt6.QtWidgets import QMessageBox
        try:
            # Update the relationship in the database with the collected data
            success = self.model_adapter.update_relationship(
                self.source_entity,
                self.relationship_type,
                self.target_entity,
                self.relationship_data
            )
            
            if success:
                # Success - close dialog without message, user can see changes immediately
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    f"Failed to save relationship details to the database."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Error saving relationship: {str(e)}"
            )
    
    def get_relationship_data(self) -> dict:
        """Get the collected relationship data"""
        return self.relationship_data