"""Relationship details dialog for viewing and editing relationship specifics"""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
)

from storymaster.model.lorekeeper.entity_mappings import get_entity_mapping
from storymaster.view.common.theme import (
    COLORS,
    get_button_style,
    get_checkbox_style,
    get_dateedit_style,
    get_dialog_style,
    get_input_style,
    get_label_style,
    get_slider_style,
    get_spinbox_style,
    get_tab_style,
)


class RelationshipDetailsDialog(QDialog):
    """Dialog for viewing and editing relationship details between entities"""

    def __init__(
        self,
        relationship_type: str,
        source_entity,
        target_entity,
        model_adapter,
        parent=None,
    ):
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

        # Apply theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_input_style()
            + get_tab_style()
            + get_spinbox_style()
            + get_slider_style()
            + get_checkbox_style()
            + get_dateedit_style()
        )

        layout = QVBoxLayout()

        # Header with relationship overview
        header = self.create_header()
        layout.addWidget(header)

        # Tabbed interface for different aspects of the relationship
        self.tab_widget = QTabWidget()

        # Basic relationship tab (only for relationship types that have basic info fields)
        if self.has_basic_info_fields():
            basic_tab = self.create_basic_tab()
            self.tab_widget.addTab(basic_tab, "Basic Info")

        # Relationship-specific tabs based on type
        if self.relationship_type == "actor_a_on_b_relations":
            self.tab_widget.addTab(
                self.create_character_relationship_tab(), "Character Dynamics"
            )
        elif self.relationship_type == "faction_members":
            self.tab_widget.addTab(self.create_membership_tab(), "Membership Details")
        elif self.relationship_type == "location_to_faction":
            self.tab_widget.addTab(self.create_territory_tab(), "Territory Control")
        elif self.relationship_type == "residents":
            self.tab_widget.addTab(self.create_residency_tab(), "Living Details")
        elif self.relationship_type == "object_to_owner":
            self.tab_widget.addTab(self.create_ownership_tab(), "Ownership Details")
        elif self.relationship_type == "actor_to_skills":
            self.tab_widget.addTab(self.create_skill_details_tab(), "Skill Details")
        elif self.relationship_type == "actor_to_class":
            self.tab_widget.addTab(
                self.create_class_details_tab(), "Profession Details"
            )
        elif self.relationship_type.startswith("history_"):
            self.tab_widget.addTab(
                self.create_historical_involvement_tab(), "Historical Context"
            )

        # Timeline/History tab (only for actor relationships that have timeline fields)
        if self.relationship_type == "actor_a_on_b_relations":
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
        details.setStyleSheet(get_label_style("small"))
        layout.addWidget(details)

        # Relationship type explanation
        explanation = self.get_relationship_explanation()
        if explanation:
            explanation_label = QLabel(explanation)
            explanation_label.setWordWrap(True)
            explanation_label.setStyleSheet(
                "color: #888; font-style: italic; margin: 8px 0;"
            )
            layout.addWidget(explanation_label)

        header.setLayout(layout)
        return header

    def has_basic_info_fields(self) -> bool:
        """Check if this relationship type has basic info fields in the database"""
        # After migration, ALL relationship types now have basic info fields
        return True

    def create_basic_tab(self) -> QGroupBox:
        """Create the basic relationship information tab"""
        tab = QGroupBox()
        layout = QFormLayout()

        # Relationship status - customized by type
        self.status_combo = QComboBox()
        status_options = self.get_status_options_for_type()
        self.status_combo.addItems(status_options)
        layout.addRow("Status:", self.status_combo)

        # Relationship strength/intensity - customized by type
        strength_info = self.get_strength_info_for_type()
        self.strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.strength_slider.setRange(strength_info["min"], strength_info["max"])
        self.strength_slider.setValue(strength_info["default"])
        self.strength_label = QLabel(str(strength_info["default"]))
        self.strength_slider.valueChanged.connect(
            lambda v: self.strength_label.setText(str(v))
        )

        strength_layout = QHBoxLayout()
        strength_layout.addWidget(self.strength_slider)
        strength_layout.addWidget(self.strength_label)

        # Add description for what the slider means
        strength_desc = QLabel(strength_info["description"])
        strength_desc.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        strength_desc.setWordWrap(True)

        strength_container = QVBoxLayout()
        strength_container.addLayout(strength_layout)
        strength_container.addWidget(strength_desc)

        layout.addRow(f"{strength_info['label']}:", strength_container)

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
        self.char_relationship_type.addItems(
            [
                "Friend",
                "Enemy",
                "Family",
                "Romantic",
                "Professional",
                "Mentor/Student",
                "Rival",
                "Ally",
                "Neutral",
                "Complicated",
            ]
        )
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
        self.trust_slider.valueChanged.connect(
            lambda v: self.trust_label.setText(str(v))
        )

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
        self.shared_history_edit.setPlaceholderText(
            "What experiences have they shared?"
        )
        layout.addRow("Shared History:", self.shared_history_edit)

        # Current status
        self.current_status_edit = QLineEdit()
        self.current_status_edit.setPlaceholderText(
            "Current state of their relationship"
        )
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
        self.loyalty_slider.valueChanged.connect(
            lambda v: self.loyalty_label.setText(str(v))
        )

        loyalty_layout = QHBoxLayout()
        loyalty_layout.addWidget(self.loyalty_slider)
        loyalty_layout.addWidget(self.loyalty_label)
        layout.addRow("Loyalty:", loyalty_layout)

        # Responsibilities
        self.responsibilities_edit = QTextEdit()
        self.responsibilities_edit.setMaximumHeight(80)
        self.responsibilities_edit.setPlaceholderText(
            "What are their responsibilities?"
        )
        layout.addRow("Responsibilities:", self.responsibilities_edit)

        # Status
        self.membership_status = QComboBox()
        self.membership_status.addItems(
            [
                "Active Member",
                "Inactive",
                "On Leave",
                "Probation",
                "Leadership",
                "Founder",
                "Honorary",
                "Former Member",
            ]
        )
        layout.addRow("Membership Status:", self.membership_status)

        tab.setLayout(layout)
        return tab

    def create_territory_tab(self) -> QGroupBox:
        """Create tab for location-faction territory control"""
        tab = QGroupBox()
        layout = QFormLayout()

        # Control type
        self.control_type = QComboBox()
        self.control_type.addItems(
            [
                "Full Control",
                "Partial Control",
                "Influence",
                "Presence",
                "Claims",
                "Disputed",
                "Historical",
                "Temporary",
            ]
        )
        layout.addRow("Control Type:", self.control_type)

        # Control strength
        self.control_strength = QSlider(Qt.Orientation.Horizontal)
        self.control_strength.setRange(1, 10)
        self.control_strength.setValue(5)
        self.control_strength_label = QLabel("5")
        self.control_strength.valueChanged.connect(
            lambda v: self.control_strength_label.setText(str(v))
        )

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
        self.resources_edit.setPlaceholderText(
            "What resources or benefits does this provide?"
        )
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
        self.involvement_level.addItems(
            [
                "Central Figure",
                "Major Participant",
                "Minor Participant",
                "Witness",
                "Affected Party",
                "Catalyst",
                "Victim",
                "Hero",
            ]
        )
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
        self.consequences_edit.setPlaceholderText(
            "What were the consequences for them?"
        )
        layout.addRow("Consequences:", self.consequences_edit)

        tab.setLayout(layout)
        return tab

    def create_residency_tab(self) -> QGroupBox:
        """Create tab for character residence details"""
        tab = QGroupBox()
        layout = QFormLayout()

        # Residence type
        self.residence_type = QComboBox()
        self.residence_type.addItems(
            [
                "Primary Home",
                "Secondary Home",
                "Temporary Stay",
                "Hideout",
                "Workplace",
                "Ancestral Home",
                "Refuge",
                "Prison",
            ]
        )
        layout.addRow("Residence Type:", self.residence_type)

        # Duration of stay
        self.duration_edit = QLineEdit()
        self.duration_edit.setPlaceholderText("How long have they lived here?")
        layout.addRow("Duration:", self.duration_edit)

        # Living conditions
        self.conditions_edit = QTextEdit()
        self.conditions_edit.setMaximumHeight(80)
        self.conditions_edit.setPlaceholderText(
            "What are their living conditions like?"
        )
        layout.addRow("Conditions:", self.conditions_edit)

        # Reason for living here
        self.reason_edit = QTextEdit()
        self.reason_edit.setMaximumHeight(80)
        self.reason_edit.setPlaceholderText("Why do they live here?")
        layout.addRow("Reason:", self.reason_edit)

        tab.setLayout(layout)
        return tab

    def create_ownership_tab(self) -> QGroupBox:
        """Create tab for item ownership details"""
        tab = QGroupBox()
        layout = QFormLayout()

        # How acquired
        self.acquisition_method = QComboBox()
        self.acquisition_method.addItems(
            [
                "Purchased",
                "Inherited",
                "Found",
                "Gifted",
                "Stolen",
                "Crafted",
                "Earned",
                "Borrowed",
                "Traded",
            ]
        )
        layout.addRow("How Acquired:", self.acquisition_method)

        # When acquired
        self.acquisition_date = QLineEdit()
        self.acquisition_date.setPlaceholderText("When did they get this item?")
        layout.addRow("When Acquired:", self.acquisition_date)

        # Current condition
        self.item_condition = QComboBox()
        self.item_condition.addItems(
            ["Excellent", "Good", "Fair", "Poor", "Damaged", "Broken", "Lost"]
        )
        layout.addRow("Condition:", self.item_condition)

        # Usage frequency
        self.usage_frequency = QComboBox()
        self.usage_frequency.addItems(
            ["Daily", "Weekly", "Monthly", "Rarely", "Never", "Special Occasions"]
        )
        layout.addRow("Usage:", self.usage_frequency)

        # Acquisition story
        self.acquisition_story = QTextEdit()
        self.acquisition_story.setMaximumHeight(80)
        self.acquisition_story.setPlaceholderText(
            "Tell the story of how they got this item..."
        )
        layout.addRow("Acquisition Story:", self.acquisition_story)

        tab.setLayout(layout)
        return tab

    def create_skill_details_tab(self) -> QGroupBox:
        """Create tab for skill proficiency details"""
        tab = QGroupBox()
        layout = QFormLayout()

        # How learned
        self.learning_method = QComboBox()
        self.learning_method.addItems(
            [
                "Self-taught",
                "Formal Training",
                "Mentor",
                "Apprenticeship",
                "Natural Talent",
                "Trial by Fire",
                "Books/Study",
                "Experimentation",
            ]
        )
        layout.addRow("How Learned:", self.learning_method)

        # Years of experience
        self.experience_years = QSpinBox()
        self.experience_years.setRange(0, 100)
        self.experience_years.setValue(1)
        layout.addRow("Years Experience:", self.experience_years)

        # Specializations
        self.specializations_edit = QLineEdit()
        self.specializations_edit.setPlaceholderText("Any special areas of expertise?")
        layout.addRow("Specializations:", self.specializations_edit)

        # Learning story
        self.learning_story = QTextEdit()
        self.learning_story.setMaximumHeight(80)
        self.learning_story.setPlaceholderText("How did they learn this skill?")
        layout.addRow("Learning Story:", self.learning_story)

        # Current practice
        self.practice_frequency = QComboBox()
        self.practice_frequency.addItems(
            ["Daily", "Weekly", "Monthly", "Rarely", "No longer practices"]
        )
        layout.addRow("Practice Frequency:", self.practice_frequency)

        tab.setLayout(layout)
        return tab

    def create_class_details_tab(self) -> QGroupBox:
        """Create tab for class/profession details"""
        tab = QGroupBox()
        layout = QFormLayout()

        # Current level/rank
        self.class_level = QSpinBox()
        self.class_level.setRange(1, 20)
        self.class_level.setValue(1)
        layout.addRow("Level/Rank:", self.class_level)

        # Experience points (if applicable)
        self.experience_points = QSpinBox()
        self.experience_points.setRange(0, 999999)
        self.experience_points.setValue(0)
        layout.addRow("Experience Points:", self.experience_points)

        # Specialization/Path
        self.specialization_edit = QLineEdit()
        self.specialization_edit.setPlaceholderText("Any specialization or path?")
        layout.addRow("Specialization:", self.specialization_edit)

        # Training/Education
        self.training_edit = QTextEdit()
        self.training_edit.setMaximumHeight(80)
        self.training_edit.setPlaceholderText("Where and how were they trained?")
        layout.addRow("Training:", self.training_edit)

        # Notable achievements
        self.achievements_edit = QTextEdit()
        self.achievements_edit.setMaximumHeight(80)
        self.achievements_edit.setPlaceholderText(
            "Any notable achievements in this profession?"
        )
        layout.addRow("Achievements:", self.achievements_edit)

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

    def get_status_options_for_type(self) -> list[str]:
        """Get status options appropriate for this relationship type"""
        status_options = {
            "actor_a_on_b_relations": [
                "Close Friends",
                "Friends",
                "Acquaintances",
                "Neutral",
                "Tension",
                "Enemies",
                "Former Friends",
                "It's Complicated",
            ],
            "faction_members": [
                "Active Member",
                "Inactive",
                "On Leave",
                "Probationary",
                "Leadership",
                "Founding Member",
                "Honorary",
                "Former Member",
            ],
            "residents": [
                "Permanent Resident",
                "Temporary",
                "Frequent Visitor",
                "Occasional Visitor",
                "Former Resident",
                "Exiled",
            ],
            "location_to_faction": [
                "Full Control",
                "Strong Presence",
                "Moderate Influence",
                "Minor Presence",
                "Contested",
                "Former Territory",
                "Claims Only",
            ],
            "history_actor": [
                "Central Figure",
                "Major Participant",
                "Minor Role",
                "Witness",
                "Affected Party",
                "Catalyst",
            ],
            "history_faction": [
                "Primary Actor",
                "Allied",
                "Opposition",
                "Neutral",
                "Victim",
                "Beneficiary",
            ],
            "object_to_owner": [
                "Owns",
                "Borrowed",
                "Stolen",
                "Inherited",
                "Found",
                "Gifted",
                "Lost",
                "Sold",
            ],
        }

        return status_options.get(
            self.relationship_type,
            ["Active", "Inactive", "Historical", "Potential", "Complicated"],
        )

    def get_strength_info_for_type(self) -> dict:
        """Get strength field configuration for this relationship type"""
        strength_configs = {
            "actor_a_on_b_relations": {
                "label": "Bond Intensity",
                "description": "How strong is their emotional connection? (1=Barely know each other, 10=Inseparable)",
                "min": 1,
                "max": 10,
                "default": 5,
            },
            "faction_members": {
                "label": "Loyalty Level",
                "description": "How devoted are they to the organization? (1=Disloyal, 10=Absolutely devoted)",
                "min": 1,
                "max": 10,
                "default": 7,
            },
            "residents": {
                "label": "Attachment Level",
                "description": "How connected are they to this place? (1=Temporary stay, 10=Deep roots)",
                "min": 1,
                "max": 10,
                "default": 5,
            },
            "location_to_faction": {
                "label": "Control Level",
                "description": "How much control does the faction have? (1=Minimal influence, 10=Complete control)",
                "min": 1,
                "max": 10,
                "default": 5,
            },
            "history_actor": {
                "label": "Impact Significance",
                "description": "How significant was this event for them? (1=Minor impact, 10=Life-changing)",
                "min": 1,
                "max": 10,
                "default": 5,
            },
            "history_faction": {
                "label": "Organizational Impact",
                "description": "How much did this event affect the organization? (1=Minor, 10=Transformative)",
                "min": 1,
                "max": 10,
                "default": 5,
            },
            "object_to_owner": {
                "label": "Attachment Level",
                "description": "How important is this item to them? (1=Hardly cares, 10=Extremely precious)",
                "min": 1,
                "max": 10,
                "default": 5,
            },
            "actor_to_skills": {
                "label": "Skill Level",
                "description": "How proficient are they? (1=Novice, 10=Master)",
                "min": 1,
                "max": 10,
                "default": 3,
            },
            "actor_to_race": {
                "label": "Heritage Strength",
                "description": "How strongly do they identify with this heritage? (1=Barely, 10=Completely)",
                "min": 1,
                "max": 10,
                "default": 8,
            },
            "actor_to_class": {
                "label": "Class Level",
                "description": "What level are they in this profession? (1=Apprentice, 10=Grandmaster)",
                "min": 1,
                "max": 20,
                "default": 5,
            },
        }

        return strength_configs.get(
            self.relationship_type,
            {
                "label": "Strength",
                "description": "General relationship strength (1=Weak, 10=Strong)",
                "min": 1,
                "max": 10,
                "default": 5,
            },
        )

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
                self.source_entity, self.relationship_type, self.target_entity
            )

            if existing_data:
                # Parse and populate the form fields with existing data
                if self.relationship_type == "actor_a_on_b_relations":
                    self.parse_actor_relationship_data(existing_data)
                elif self.relationship_type == "faction_a_on_b_relations":
                    self.parse_faction_relationship_data(existing_data)
                elif self.relationship_type == "faction_members":
                    self.parse_membership_data(existing_data)
                elif self.relationship_type == "location_to_faction":
                    self.parse_location_to_faction_data(existing_data)
                elif self.relationship_type == "residents":
                    self.parse_residents_data(existing_data)
                elif self.relationship_type == "object_to_owner":
                    self.parse_object_to_owner_data(existing_data)
                elif self.relationship_type == "actor_to_skills":
                    self.parse_actor_to_skills_data(existing_data)
                elif self.relationship_type == "actor_to_race":
                    self.parse_actor_to_race_data(existing_data)
                elif self.relationship_type == "actor_to_class":
                    self.parse_actor_to_class_data(existing_data)
                elif self.relationship_type == "actor_to_stat":
                    self.parse_actor_to_stat_data(existing_data)
                elif self.relationship_type == "history_actor":
                    self.parse_history_actor_data(existing_data)
                elif self.relationship_type == "history_location":
                    self.parse_history_location_data(existing_data)
                elif self.relationship_type == "history_faction":
                    self.parse_history_faction_data(existing_data)
                else:
                    # No parser available for this relationship type
                    pass

        except Exception as e:
            print(f"Error loading relationship data: {e}")
            # Continue with default values if loading fails

    def parse_actor_relationship_data(self, data):
        """Parse actor relationship data from database format"""
        # Use new structured fields directly
        self.description_edit.setPlainText(data.get("description", ""))
        self.notes_edit.setPlainText(data.get("notes", ""))
        self.timeline_edit.setPlainText(data.get("timeline", ""))
        self.how_met_edit.setPlainText(data.get("how_met", ""))
        self.shared_history_edit.setPlainText(data.get("shared_history", ""))
        self.current_status_edit.setText(data.get("current_status", ""))

        # Set relationship type
        rel_type = data.get("relationship_type", "")
        if rel_type:
            index = self.char_relationship_type.findText(rel_type)
            if index >= 0:
                self.char_relationship_type.setCurrentIndex(index)

        # Set status
        status = data.get("status", "")
        if status:
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)

        # Set sliders
        self.strength_slider.setValue(data.get("strength", 5))
        self.trust_slider.setValue(data.get("trust_level", 5))

        # Set checkboxes
        self.is_mutual.setChecked(data.get("is_mutual", True))
        self.is_public.setChecked(data.get("is_public", True))

    def parse_faction_relationship_data(self, data):
        """Parse faction-to-faction relationship data from database format"""
        # Basic Info fields (description, notes are in Basic Info tab)
        if hasattr(self, "description_edit"):
            self.description_edit.setPlainText(data.get("description", ""))

        if hasattr(self, "notes_edit"):
            self.notes_edit.setPlainText(data.get("notes", ""))

        # Set status combo
        status = data.get("status", "")
        if status and hasattr(self, "status_combo"):
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)

        # Set strength slider
        if hasattr(self, "strength_slider"):
            strength = data.get("strength", 5)
            self.strength_slider.setValue(strength)

        # Set is_public checkbox
        if hasattr(self, "is_public"):
            is_public = data.get("is_public", True)
            self.is_public.setChecked(is_public)

    def parse_membership_data(self, data):
        """Parse faction membership data from database format"""
        # Use new structured fields directly
        self.role_edit.setText(data.get("role", ""))
        self.rank_spin.setValue(data.get("rank", 1))
        self.responsibilities_edit.setPlainText(data.get("responsibilities", ""))
        self.loyalty_slider.setValue(data.get("loyalty", 7))

        # Set membership status
        membership_status = data.get("membership_status", "")
        if membership_status:
            index = self.membership_status.findText(membership_status)
            if index >= 0:
                self.membership_status.setCurrentIndex(index)

        # Set join date if available
        join_date = data.get("join_date", "")
        if join_date:
            # Parse join date string and set the date widget
            # For now, just store it as string format
            pass

    def parse_location_to_faction_data(self, data):
        """Parse location-to-faction relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Territory-specific fields would go here when UI supports them

    def parse_residents_data(self, data):
        """Parse resident relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Residency-specific fields would go here when UI supports them

    def parse_object_to_owner_data(self, data):
        """Parse object ownership relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Ownership-specific fields would go here when UI supports them

    def parse_actor_to_skills_data(self, data):
        """Parse actor-to-skills relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Skill-specific fields would go here when UI supports them

    def parse_actor_to_race_data(self, data):
        """Parse actor-to-race relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Heritage-specific fields would go here when UI supports them

    def parse_actor_to_class_data(self, data):
        """Parse actor-to-class relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Class-specific fields would go here when UI supports them

    def parse_actor_to_stat_data(self, data):
        """Parse actor-to-stat relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Stat-specific fields would go here when UI supports them

    def parse_history_actor_data(self, data):
        """Parse history-actor relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Historical involvement fields would go here when UI supports them

    def parse_history_location_data(self, data):
        """Parse history-location relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Historical location fields would go here when UI supports them

    def parse_history_faction_data(self, data):
        """Parse history-faction relationship data from database format"""
        self._parse_basic_relationship_data(data)
        # Historical faction fields would go here when UI supports them

    def _parse_basic_relationship_data(self, data):
        """Helper method to parse common basic relationship fields"""
        # Basic Info fields (description, notes are in Basic Info tab)
        if hasattr(self, "description_edit"):
            description = data.get("description", "")
            self.description_edit.setPlainText(description)

        if hasattr(self, "notes_edit"):
            notes = data.get("notes", "")
            self.notes_edit.setPlainText(notes)

        # Set status combo
        status = data.get("status", "")
        if status and hasattr(self, "status_combo"):
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)

        # Set strength slider
        if hasattr(self, "strength_slider"):
            strength = data.get("strength", 5)
            self.strength_slider.setValue(strength)

        # Set is_public checkbox
        if hasattr(self, "is_public"):
            is_public = data.get("is_public", True)
            self.is_public.setChecked(is_public)

    def save_relationship(self):
        """Save the relationship data"""
        # Initialize relationship data
        self.relationship_data = {}

        # Collect basic info data for relationship types that support it
        if self.has_basic_info_fields():
            self.relationship_data.update(
                {
                    "status": self.status_combo.currentText(),
                    "strength": self.strength_slider.value(),
                    "description": self.description_edit.toPlainText(),
                    "notes": self.notes_edit.toPlainText(),
                    "is_public": self.is_public.isChecked(),
                }
            )
            # Add timeline field if it exists (only for some relationship types)
            if hasattr(self, "timeline_edit"):
                self.relationship_data["timeline"] = self.timeline_edit.toPlainText()

        # Add relationship-specific data
        if self.relationship_type == "actor_a_on_b_relations":
            self.relationship_data.update(
                {
                    # Character relationship specific fields
                    "relationship_type": self.char_relationship_type.currentText(),
                    "is_mutual": self.is_mutual.isChecked(),
                    "trust_level": self.trust_slider.value(),
                    "how_met": self.how_met_edit.toPlainText(),
                    "shared_history": self.shared_history_edit.toPlainText(),
                    "current_status": self.current_status_edit.text(),
                }
            )
        elif self.relationship_type == "faction_members":
            self.relationship_data.update(
                {
                    "role": self.role_edit.text(),
                    "rank": self.rank_spin.value(),
                    "join_date": self.join_date.date().toString(),
                    "loyalty": self.loyalty_slider.value(),
                    "responsibilities": self.responsibilities_edit.toPlainText(),
                    "membership_status": self.membership_status.currentText(),
                }
            )

        # Actually save to the database
        from PySide6.QtWidgets import QMessageBox

        try:
            # Update the relationship in the database with the collected data
            success = self.model_adapter.update_relationship(
                self.source_entity,
                self.relationship_type,
                self.target_entity,
                self.relationship_data,
            )

            if success:
                # Success - close dialog without message, user can see changes immediately
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    f"Failed to save relationship details to the database.\n\nRelationship Type: {self.relationship_type}\nCheck console for details.",
                )
        except Exception as e:
            print(f"💥 Save error: {str(e)}")
            import traceback

            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Database Error",
                f"Error saving relationship: {str(e)}\n\nRelationship Type: {self.relationship_type}\nCheck console for detailed error information.",
            )

    def get_relationship_data(self) -> dict:
        """Get the collected relationship data"""
        return self.relationship_data
