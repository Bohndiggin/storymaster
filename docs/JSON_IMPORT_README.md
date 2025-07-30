# Universal JSON Story Import System

This system allows you to import story data into Storymaster from a JSON file. It's designed to be universal and LLM-friendly, making it easy for AI systems to generate complete story worlds.

## Files

- `story_schema_template.json` - Template with blank entries for all database tables
- `import_from_json.py` - Python script to import JSON data into the database
- `sample_story.json` - Example story data demonstrating the format

## How It Works

1. **JSON Structure**: The JSON file contains one key for each database table, with an array of row objects
2. **Foreign Key Ordering**: Tables are ordered to satisfy foreign key dependencies
3. **Blank Templates**: Each table has a template row with appropriate default values
4. **LLM Integration**: An LLM can fill out the template with story details

## Usage

### Basic Import
```bash
python import_from_json.py your_story.json
```

### Creating Story Data

1. **Start with the template**: Copy `story_schema_template.json`
2. **Fill in your data**: Replace empty strings and default values with your story content
3. **Maintain relationships**: Ensure foreign key IDs match between related tables
4. **Import**: Run the import script

### Key Rules

- **IDs must be consistent**: If Actor ID 1 is referenced in relationships, make sure Actor with ID 1 exists
- **Required fields**: Some fields like `user_id`, `setting_id` are required for most tables
- **Empty arrays are OK**: Tables with no data can be left as empty arrays `[]`
- **Null values**: Use `null` for truly empty fields, empty strings `""` for text fields

## LLM Integration

This system is designed for LLM use. An LLM can:

1. Take the template JSON
2. Fill it out with story details based on a prompt
3. Ensure foreign key relationships are consistent
4. Generate a complete, importable story world

### Example LLM Prompt

```
Please fill out this Storymaster JSON template with a fantasy story about [your story concept]. 
Ensure all foreign key relationships are consistent (if you reference actor_id: 1 in a relationship, 
make sure there's an actor with id: 1). Focus on creating compelling characters, interesting locations, 
and meaningful relationships between story elements.
```

## Database Schema Overview

### Core Tables (Required)
- `user` - System user (usually just one)
- `setting` - The story world/universe
- `storyline` - Individual stories within the setting
- `storyline_to_setting` - Links stories to their worlds

### Character System
- `actor` - Characters in your story
- `alignment` - Moral/ethical alignments
- `background` - Character backgrounds/origins
- `class` - Character classes/professions
- `race`/`sub_race` - Character species/ethnicities
- `stat` - Character attributes
- `skills` - Character abilities

### World Building
- `location_` - Places in your world
- `faction` - Organizations and groups
- `history` - Historical events
- `object_` - Important items/artifacts
- `world_data` - General world information

### Relationships
- Various `*_to_*` and `*_relations` tables link the above entities
- Example: `actor_a_on_b_relations` defines how characters relate to each other

### Story Structure (Litographer)
- `litography_node` - Story beats/scenes
- `litography_arc` - Character/story arcs
- `litography_plot` - Plot structures
- Various connection tables link these elements

## Tips for Success

1. **Start simple**: Begin with basic entities (user, setting, storyline) and build up
2. **Plan relationships**: Think about how your characters, locations, and factions connect
3. **Use meaningful IDs**: Keep track of which ID numbers you've used for each table
4. **Test incrementally**: Import and verify your data works before adding more complexity
5. **Leverage the sample**: Use `sample_story.json` as a reference for proper formatting

## Troubleshooting

### Common Errors
- **Foreign key constraint failures**: Make sure referenced IDs exist in their parent tables
- **Missing required fields**: Check that `user_id`, `setting_id` are provided where needed
- **Invalid enum values**: Some fields like `node_type` only accept specific values

### Error Messages
The import script provides detailed error messages showing which table and row caused problems.

## Advanced Usage

### Custom Import Logic
You can modify `import_from_json.py` to add custom validation or transformation logic.

### Partial Imports
Set `clear_db=False` in the `import_from_json()` function to append to existing data instead of replacing it.

### Multiple Settings
You can have multiple settings (story worlds) in the same database by using different `setting_id` values.