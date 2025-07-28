"""
Comprehensive tooltip system for Storymaster UI components
Provides helpful explanations and guidance for all form fields and UI elements
"""

# Lorekeeper Entity Field Tooltips
LOREKEEPER_TOOLTIPS = {
    # Actor/Character fields
    "actor_first_name": "The character's given name or first name. This will be used throughout the story references.",
    "actor_last_name": "The character's family name or surname. Optional but helps with character organization.",
    "actor_age": "The character's age in years. Can be approximate (e.g., 'early 30s') or specific.",
    "actor_description": "A detailed physical and personality description of the character. Include appearance, mannerisms, and key traits.",
    "actor_background": "The character's backstory, history, and formative experiences that shaped who they are.",
    "actor_motivation": "What drives this character? Their primary goals, desires, and what they want to achieve.",
    "actor_occupation": "The character's job, profession, or role in society. This affects their skills and knowledge.",
    "actor_relationships": "Key relationships with other characters, family members, or important people in their life.",
    # Location fields
    "location_name": "The name of this place. Be specific and memorable (e.g., 'The Rusted Crown Tavern' vs 'tavern').",
    "location_description": "Detailed description of the location's appearance, atmosphere, and important features.",
    "location_history": "The background and past events that occurred at this location. What makes it significant?",
    "location_climate": "The weather patterns, seasons, and environmental conditions of this location.",
    "location_government": "How this place is ruled or governed. Who's in charge and what are the laws?",
    "location_economy": "What drives the local economy? Trade, agriculture, industry, or natural resources?",
    "location_culture": "The customs, traditions, and way of life of the people who live here.",
    "location_population": "How many people live here? Is it a small village, bustling city, or something in between?",
    # Faction fields
    "faction_name": "The name of this group, organization, or faction. Make it memorable and fitting for their purpose.",
    "faction_description": "What this faction is about, their public face, and how others perceive them.",
    "faction_goals": "What does this faction want to achieve? Their primary objectives and long-term plans.",
    "faction_methods": "How does this faction operate? Are they subtle, aggressive, diplomatic, or secretive?",
    "faction_resources": "What assets does this faction have? Money, people, influence, magic, technology?",
    "faction_allies": "Other factions, organizations, or individuals that support or work with this group.",
    "faction_enemies": "Who opposes this faction? Their rivals, enemies, or those with conflicting interests.",
    "faction_structure": "How is this faction organized? Is it hierarchical, democratic, or loosely affiliated?",
    # Object fields
    "object_name": "The name of this item, artifact, or important object in your story world.",
    "object_description": "What does this object look like? Include size, materials, craftsmanship, and notable features.",
    "object_history": "The origin and past of this object. Who made it, owned it, or used it? Any legendary events?",
    "object_properties": "Special abilities, magical properties, or unique characteristics of this object.",
    "object_value": "How valuable is this object? Monetary worth, rarity, or significance to certain groups.",
    "object_location": "Where is this object currently located? Who has possession of it?",
    "object_significance": "Why is this object important to your story? How does it affect the plot or characters?",
    # World Data fields
    "world_data_title": "A clear, descriptive title for this piece of world information.",
    "world_data_content": "Detailed information about this aspect of your world. Be comprehensive and specific.",
    "world_data_category": "What type of world-building information is this? (Religion, Magic System, Technology, etc.)",
    "world_data_relevance": "How does this information impact your story? Why is it important to track?",
    # Common relationship fields
    "relationship_type": "The nature of the relationship between these entities. How are they connected?",
    "relationship_description": "Details about this relationship. How did it form? What characterizes it?",
    "relationship_status": "The current state of this relationship. Is it active, strained, secret, or changing?",
}

# Litographer (Story Structure) Tooltips
LITOGRAPHER_TOOLTIPS = {
    # Node creation and editing
    "node_type": "Choose the type of story beat this node represents. Different shapes help visualize story flow.",
    "node_label": "A brief, memorable name for this story beat (e.g., 'Hero meets mentor', 'Dark moment').",
    "node_description": "Detailed description of what happens in this part of the story. Include key events and character actions.",
    "node_tension": "How intense or important is this moment? Higher tension nodes appear taller in the visual layout.",
    "node_connections": "How this story beat connects to other parts of your plot. Consider cause and effect relationships.",
    # Plot structure
    "plot_title": "The name of this plot line. You can have multiple plots for subplots and character arcs.",
    "plot_description": "What is this plot about? The main conflict, journey, or story thread it represents.",
    "plot_sections": "Organizational containers that help group related story beats together (Act 1, Rising Action, etc.).",
    # Node types explanations
    "opening": "The beginning of your story. Sets the scene, introduces characters, and establishes the normal world.",
    "inciting_incident": "The event that kicks off the main conflict and propels your protagonist into the story.",
    "plot_point": "Major turning points that change the direction of your story and raise the stakes.",
    "midpoint": "The crucial middle moment that shifts the story's focus and often reveals new information.",
    "climax": "The peak of your story's conflict where the main tension reaches its highest point.",
    "resolution": "How conflicts are resolved and loose ends are tied up. The new normal after the story events.",
    "character_moment": "Scenes focused on character development, relationships, or internal growth.",
    "action": "High-energy scenes with physical conflict, chases, battles, or other dynamic events.",
    "dialogue": "Conversation-heavy scenes that reveal character, advance plot, or provide exposition.",
    "transition": "Bridging scenes that move the story from one location, time, or situation to another.",
}

# Character Arc Management Tooltips
CHARACTER_ARC_TOOLTIPS = {
    # Arc creation
    "arc_title": "A descriptive name for this character's journey (e.g., 'Sarah's revenge quest', 'John learns to trust').",
    "arc_description": "Overview of this character's emotional and personal journey throughout the story.",
    "arc_type": "The category or pattern of this character arc (Hero's Journey, Redemption, Fall from Grace, etc.).",
    "arc_characters": "Which characters are involved in this arc? Main character and supporting characters.",
    # Arc points
    "arc_point_title": "A brief name for this point in the character's journey (e.g., 'Refuses the call', 'Faces fear').",
    "arc_point_description": "What happens to the character at this point? How do they grow or change?",
    "arc_point_order": "The sequence number of this point in the character's arc. Lower numbers come first.",
    "arc_point_emotional_state": "How is the character feeling at this point? Their internal emotional condition.",
    "arc_point_relationships": "How do the character's relationships change or develop at this point?",
    "arc_point_goals": "What does the character want to achieve at this stage of their journey?",
    "arc_point_conflict": "Internal struggles, doubts, or conflicts the character faces at this point.",
    "arc_point_node": "Which story node (from Litographer) does this character development occur in?",
}

# Main Navigation and General UI Tooltips
GENERAL_UI_TOOLTIPS = {
    # Main navigation
    "litographer_tab": "Visual story structure planning. Create and connect story beats to map out your plot.",
    "lorekeeper_tab": "World-building database. Manage characters, locations, factions, and story elements.",
    "character_arcs_tab": "Character development tracking. Plan emotional journeys and character growth arcs.",
    # Common actions
    "save_button": "Save your changes to the database. All information will be preserved for future sessions.",
    "delete_button": "Permanently remove this item. This action cannot be undone, so use with caution.",
    "edit_button": "Modify the information for this item. Opens a form where you can update details.",
    "new_button": "Create a new item of this type. Opens a blank form for you to fill in.",
    "cancel_button": "Discard any changes and close this dialog without saving anything.",
    # Database and project management
    "project_selector": "Choose which story project you're working on. Each project has its own database.",
    "backup_database": "Create a backup copy of your story data. Recommended before making major changes.",
    "import_data": "Load information from external files or other story projects.",
    "export_data": "Save your story information to files for backup or sharing with others.",
    # Search and filtering
    "search_field": "Type to search through items. Use keywords from names, descriptions, or any text content.",
    "filter_dropdown": "Narrow down the list to show only specific types or categories of items.",
    "sort_options": "Change how items are ordered in the list (alphabetical, by date, by type, etc.).",
}

# Notes and Associations Tooltips
NOTES_TOOLTIPS = {
    "note_title": "A brief, descriptive title for this note that makes it easy to find later.",
    "note_description": "The main content of your note. This can be research, ideas, inspiration, or any relevant information.",
    "note_type": "Categorize your note to help with organization (Plot idea, Character inspiration, Research, etc.).",
    "note_associations": "Link this note to characters, locations, or other story elements it relates to.",
    "add_association": "Connect this note to story elements. Creates helpful cross-references in your world-building.",
    "remove_association": "Disconnect this note from a story element. The note remains, but the link is removed.",
}


def apply_tooltip(widget, tooltip_key, tooltip_dict=None):
    """
    Apply a tooltip to a widget based on a key

    Args:
        widget: The Qt widget to add tooltip to
        tooltip_key: The key to look up in tooltip dictionaries
        tooltip_dict: Specific tooltip dictionary to use (optional)
    """
    # Try all tooltip dictionaries if none specified
    if tooltip_dict is None:
        all_tooltips = {
            **LOREKEEPER_TOOLTIPS,
            **LITOGRAPHER_TOOLTIPS,
            **CHARACTER_ARC_TOOLTIPS,
            **GENERAL_UI_TOOLTIPS,
            **NOTES_TOOLTIPS,
        }
        tooltip_text = all_tooltips.get(tooltip_key)
    else:
        tooltip_text = tooltip_dict.get(tooltip_key)

    if tooltip_text:
        widget.setToolTip(tooltip_text)


def apply_lorekeeper_tooltips(widget, field_name):
    """Apply lorekeeper-specific tooltips"""
    apply_tooltip(widget, field_name, LOREKEEPER_TOOLTIPS)


def apply_litographer_tooltips(widget, field_name):
    """Apply litographer-specific tooltips"""
    apply_tooltip(widget, field_name, LITOGRAPHER_TOOLTIPS)


def apply_character_arc_tooltips(widget, field_name):
    """Apply character arc-specific tooltips"""
    apply_tooltip(widget, field_name, CHARACTER_ARC_TOOLTIPS)


def apply_general_tooltips(widget, field_name):
    """Apply general UI tooltips"""
    apply_tooltip(widget, field_name, GENERAL_UI_TOOLTIPS)


def apply_notes_tooltips(widget, field_name):
    """Apply notes-specific tooltips"""
    apply_tooltip(widget, field_name, NOTES_TOOLTIPS)


# Helper function to add tooltips to form fields by pattern matching
def auto_apply_tooltips(form_widget):
    """
    Automatically apply tooltips to widgets based on their object names
    This is a convenience function for applying tooltips in bulk
    """
    # Get all child widgets
    children = form_widget.findChildren(type(form_widget.children()[0]))

    for child in children:
        object_name = child.objectName()
        if object_name:
            # Try to match common patterns and apply appropriate tooltips
            apply_tooltip(child, object_name)
