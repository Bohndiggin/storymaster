# Storymaster

A comprehensive creative writing tool that combines visual story plotting with detailed world-building capabilities.

## Overview

Storymaster is a PyQt6-based desktop application designed for writers who want to plan and organize complex stories. It provides two integrated modules:

- **Litographer**: Visual story structure planning using an interactive node-based graph
- **Lorekeeper**: Comprehensive world-building database for managing characters, locations, factions, and their relationships

## Features

### Litographer (Story Plotting)
- **Visual Story Structure**: Create story beats as connected nodes in a visual graph
- **Node Types**: Different shapes represent story elements (Exposition, Action, Reaction, Twist, Development)
- **Plot Sections**: Organize your story into sections with different tension types
- **Linked Navigation**: Nodes connect in sequence, showing story flow
- **Interactive Editing**: Click nodes to edit properties, add/delete with visual buttons

### Lorekeeper (World Building)
- **Character Management**: Detailed actor profiles with relationships and faction memberships
- **Location Tracking**: Hierarchical location system (cities, districts, dungeons)
- **Faction Systems**: Complex organization relationships and politics
- **Historical Events**: Timeline management with multi-entity involvement
- **Object Cataloging**: Items, artifacts, and world elements
- **Dynamic Forms**: Database-driven interface adapts to your data structure

## Requirements

- Python 3.8+
- PostgreSQL database
- PyQt6

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd writing-tools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your database connections:
```
DATABASE_CONNECTION="postgresql://username:password@host:port/database_name"
TEST_DATABASE_CONNECTION="postgresql://username:password@host:port/test_database_name"
```

4. Initialize the database:
```bash
python seed.py
```

## Usage

Run the application:
```bash
python storymaster/main.py
```

### Getting Started

1. **Litographer Mode**: Start by creating your first story node using the "+" button
2. **Plot Sections**: Organize your story into sections (Beginning, Middle, End, etc.)
3. **Node Connections**: Link story beats in sequence to show narrative flow
4. **Lorekeeper Mode**: Switch to build your world's characters, locations, and factions
5. **Cross-References**: Use the relationship system to connect world elements

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Database Management
The application uses SQLAlchemy with PostgreSQL. Test data can be seeded using the provided CSV files in `tests/model/database/test_data/`.

## Architecture

- **MVC Pattern**: Clean separation of Model (SQLAlchemy), View (PyQt6), and Controller layers
- **Modular Design**: Separate modules for plotting (Litographer) and world-building (Lorekeeper)
- **Database-Driven**: Comprehensive schema supporting complex relationships and story structures

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure code formatting with Black
6. Submit a pull request

## License

[Add your license information here]