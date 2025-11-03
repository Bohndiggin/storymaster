# Storymaster User Guide

**Storymaster** is a comprehensive creative writing tool that helps you plan stories and build worlds. It combines visual story plotting (Litographer) with detailed world-building (Lorekeeper) in one integrated application.

## Download

[![Download QR Code](qr_code_2025-10-22_14-42-07_UTC.png)](https://github.com/Bohndiggin/storymaster/releases)

**[Download Latest Release](https://github.com/Bohndiggin/storymaster/releases)**

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Getting Started](#getting-started)
3. [Litographer - Story Mapper](#litographer---story-mapper)
4. [Lorekeeper - Lore Manager](#lorekeeper---lore-manager)
5. [Character Arc Page](#character-arc-page)
6. [Tips & Best Practices](#tips--best-practices)

---

## Core Concepts

### Project Hierarchy

```
User
└── Setting (World)
    ├── Storyline (Plot)
    │   ├── Section
    │   │   └── Nodes (Plot Points)
    │   └── Section
    │       └── Nodes
    └── Lore (Characters, Locations, etc.)
```

### Key Terms

**Setting**: A world or universe for your stories. Multiple storylines can exist in one setting, sharing the same lore. Perfect for series, sequels, or interconnected stories.

**Storyline**: A specific plot within a setting. Composed of Sections containing Nodes that represent your story's structure.

---

## Litographer - Story Structure

### Sections

**Sections** divide your storyline into meaningful parts, similar to Aristotle's plot structure or dramatic acts. Each section has a tension type that visualizes story pacing:

| Type | Purpose | Visual |
|------|---------|--------|
| **Tension Sustains** | Maintain current tension level | Flat line: `____` |
| **Tension Increases** | Build suspense and conflict | Rising: `/` |
| **Singular Moment** | Climactic peaks or reveals | Peak: `^` |
| **Tension Lowers** | Resolution or calm periods | Falling: `\` |

**Example Story Arc**:
```
Exposition  Rising Action  Climax  Falling Action  Resolution
  ____          /            ^          \             ____
```

### Nodes

**Nodes** are individual plot points within sections. Each node represents a key story moment:

- **Exposition**: Introduce setting, characters, or context
- **Action**: Events that drive the plot forward
- **Reaction**: Character responses to events
- **Twist**: Unexpected revelations or turns
- **Development**: Character growth or relationship changes
- **Other**: Custom plot points

**Node Features**:
- Customizable shapes (rectangle, circle, diamond, star, hexagon, triangle)
- Name and description fields for detailed planning
- Visual connections showing story flow
- Support for branching narratives (many-to-many connections)

---

## Lorekeeper - World Building

### Core Lore Types

#### Characters
Create detailed character profiles with:
- **Basic Info**: Name, title, age
- **Appearance & Personality**: Physical traits and character
- **Background & Role**:
  - Backgrounds: Archetypes from the background library
  - Role: Their function in your story
- **Character Traits**:
  - Alignment: Moral compass (inspired by D&D)
  - Ideal: What they strive for
  - Bond: What ties them to the world/story
- **Relationships**: Track connections to other characters, organizations, and locations

#### Organizations
Factions, guilds, governments, companies, or any group entity. Track members, rivalries, and influence.

#### Locations
Places in your world, from continents to rooms. Note features, inhabitants, and significance.

#### Items
Objects of any scale: magic swords, spaceships, important documents, or family heirlooms.

#### Events
Historical events that shape your world. Link characters, locations, and organizations involved.

#### World Lore
General facts about your setting: magic systems, technology levels, cultural norms, natural laws.

#### Story Notes
Notes directly connected to your Litographer plot points for seamless planning.

### Supporting Categories

These help you quickly build consistent characters and worlds:

- **Backgrounds**: Archetypes (e.g., "Noble", "Street Urchin", "Soldier")
- **Heritage Types**: Races, species, or ethnic groups
- **Professions**: Available occupations in your world
- **Skills**: Abilities characters might possess

---

## Getting Started

### First Launch Setup

Storymaster guides you through initial setup automatically:

1. **Create User Profile**: Your personal account
2. **Create First Setting**: Your first world
3. **Create First Storyline**: Your first plot

Setup is one-time only. After this, you can create unlimited settings and storylines.

### Important Notes

- **Auto-Save**: Everything saves automatically in real-time
- **Local Storage**: All data stored on your computer in a local database
- **No Cloud Required**: Works completely offline
- **No Save Button**: Changes persist immediately
- **Safe to Experiment**: Your data is always preserved

### Creating Additional Content

**New Setting**: File menu → New Setting
**New Storyline**: Within a setting, create multiple storylines
**Switch Projects**: Use the menu to navigate between settings and storylines

---

## Litographer - Story Mapper

![Litographer Page](screenshots/litographer_page.png)

### Working with the Canvas

#### Adding Nodes
- **Right-click** on canvas → "Add Node"
- Fill in node name and description
- Choose node type and shape

#### Moving Nodes
- **Click and drag** nodes to reposition
- Organize visually to match your story flow

#### Connecting Nodes
- **Drag from red dot** (output) on one node
- **Drop on green dot** (input) on another node
- Creates directional story flow
- **Many-to-many connections**: Create branching narratives with multiple paths

#### Managing Sections
- Click **"+ Add Section"** to create a new story segment
- **Right-click section** → Change tension type
- Sections organize nodes and visualize story pacing
- Drag nodes into sections to group related plot points

#### Editing Content
- **Click any node** to edit its details in the side panel
- Update name, description, type, and shape
- **Delete**: Right-click → Delete

### Canvas Controls
- **Zoom**: Mouse wheel
- **Pan**: Click and drag on empty space

---

## Lorekeeper - Lore Manager

![Lorekeeper Page](screenshots/lorekeeper_page.png)

### Three-Panel Interface

#### Left Panel - Navigation
Browse and select lore entries:
- **Top dropdown**: Choose lore type (Characters, Locations, etc.)
- **Bottom list**: All entries of selected type
- **Search**: Find entries quickly
- **Add New**: Create entries with the "+" button

#### Middle Panel - Details
View and edit the selected entry:
- Complete form with all relevant fields
- Text areas for descriptions and notes
- Dropdowns for linked data (backgrounds, heritages, etc.)
- All changes auto-save

#### Right Panel - Relationships
Manage connections between lore entries:
- **Character relationships**: Friends, enemies, family, rivals
- **Organization membership**: Who belongs where
- **Location connections**: Who lives where, what's located where
- **Item ownership**: Who possesses what
- **Event participation**: Who was involved in which events

### Working with Lore

1. **Create Entry**: Select type → Click "+" → Fill form
2. **Edit Entry**: Click entry in list → Modify in middle panel
3. **Add Relationships**: Select entry → Use right panel to link
4. **Delete Entry**: Select entry → Delete button (with confirmation)
5. **Cross-reference**: Click linked items to jump to them

---

## Character Arc Page

![Character Arc Page](screenshots/character_arc_page.png)

The Character Arc page helps you track character development throughout your story. Plan how characters change, grow, and evolve from beginning to end.

---

## Tips & Best Practices

### Workflow Suggestions

1. **Start with Lore**: Build your world first (characters, locations, factions)
2. **Outline with Sections**: Create major story sections in Litographer
3. **Add Plot Points**: Fill sections with detailed nodes
4. **Connect Lore to Plot**: Link lore entries to relevant story nodes
5. **Iterate**: Refine as your story develops

### Organization Tips

- **Use Descriptive Names**: Clear node and lore names help navigation
- **Color Code**: Different node shapes help visually distinguish plot point types
- **Section Structure**: Align with classic story structure (exposition, rising action, climax, falling action, resolution)
- **Relationships Matter**: Rich character relationships create deeper stories
- **Branching Narratives**: Use multiple connections for alternate storylines or character perspectives

### Multi-Project Management

- **Series Planning**: One setting, multiple storylines
- **Shared Worlds**: Reuse lore across different plots
- **Standalone Stories**: Each with its own unique setting
- **Genre Experiments**: Switch between different settings and styles

### Backup Your Work

While Storymaster auto-saves to a local database:
- **Database Location**: `storymaster.db` in installation folder
- **Backup**: Copy this file periodically to preserve your work
- **Restore**: Replace the .db file to restore from backup

### Performance

- **Large Projects**: Storymaster handles extensive lore databases efficiently
- **Complex Plots**: No limit on nodes or connections
- **Offline Always**: No internet required, ever

---

## Need Help?

- **GitHub Issues**: [Report bugs or request features](https://github.com/Bohndiggin/storymaster/issues)
- **Documentation**: Check repository README for technical details
- **Community**: Share your stories and tips with other users

---

**Happy Writing! 📖**