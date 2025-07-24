# 🏰 Storymaster

**Visual Story Plotting & World-Building Tool**

Storymaster is a PyQt6-based creative writing application that combines visual story structure planning with comprehensive world-building capabilities.

## 🚀 Quick Install

**Prerequisites:**
- Python 3.8 or higher
- Works on Windows, macOS, and Linux

**One-command installation:**
```bash
python install.py
```

The installer will:
- ✅ Create a virtual environment
- ✅ Install all dependencies  
- ✅ Initialize SQLite database
- ✅ Optionally seed with sample data

## 🎯 Features

### 📖 Litographer - Visual Story Plotting
- **Node-based story structure** with linked-list navigation
- **Multiple plot support** - create and switch between different storylines
- **Plot sections** with tension types (Rising, Flat, Point, Lower)
- **Custom node shapes** (rectangle, circle, diamond, star, hexagon, triangle)
- **Visual connections** showing story flow
- **Integrated notes** for each story beat

### 🗂️ Lorekeeper - World Building Database
- **Character management** - actors, backgrounds, classes, races
- **Faction system** with complex relationships
- **Location tracking** with detailed descriptions
- **Historical events** with multi-entity involvement
- **Object catalog** for items and artifacts
- **Dynamic forms** with foreign key relationships

### 🔧 Technical Features
- **SQLite database** - fully offline, portable
- **Project isolation** - multiple stories in one database
- **Dark theme** UI inspired by professional tools
- **Cross-platform** compatibility

## 🏃‍♂️ Running Storymaster

After installation:

```bash
# Activate virtual environment
source .venv/bin/activate    # Linux/Mac
# or
.venv\Scripts\activate      # Windows

# Run the application
python storymaster/main.py
```

## 📁 Project Structure

```
storymaster/
├── storymaster/           # Main application code
│   ├── model/            # Database models and business logic
│   ├── view/             # PyQt6 UI components
│   └── controller/       # Event handling and coordination
├── tests/                # Test suite with sample data
├── install.py           # One-click installer
├── init_database.py     # Database initialization
├── seed.py             # Sample data loading
└── requirements.txt    # Python dependencies
```

## 🛠️ Development

### Manual Setup
If you prefer to set up manually:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_database.py

# Seed with sample data (optional)
python seed.py

# Run application
python storymaster/main.py
```

### Testing
```bash
pytest tests/
```

### Code Formatting
```bash
black .
isort .
```

## 🎨 Plot Management

Use the **Plot** menu to:
- **New Plot** - Create additional storylines
- **Switch Plot** - Move between different plots
- **Delete Plot** - Remove unused plots
- **Open Project** - Switch between different story projects

## 🗄️ Database

- **SQLite** - Single file database (`storymaster.db`)
- **Portable** - Copy the .db file to backup/share your work
- **Offline** - No internet connection required
- **Sample data** - Includes example characters, locations, and story nodes

## 🆘 Troubleshooting

**Common Issues:**

1. **"ModuleNotFoundError"** - Make sure virtual environment is activated
2. **"Database connection failed"** - Run `python init_database.py`
3. **"PyQt6 not found"** - Install with `pip install PyQt6`

**Getting Help:**
- Check the documentation
- Create an issue on GitHub
- Review the sample data to understand the data model

## 📄 License

This project is open source. See LICENSE file for details.

---

**Happy storytelling! 📚✨**