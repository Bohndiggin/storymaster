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

## 📦 Distribution & Packaging

### For Developers - Creating Distribution Packages

**Build all distribution formats:**
```bash
python build_all.py
```

**Individual build options:**
```bash
# Cross-platform executable
python build_executable.py

# Linux AppImage (universal binary)
python build_appimage.py

# Linux RPM package
python build_rpm.py
```

**Available distribution formats:**
- **Executable** - Standalone binary with Python runtime included
- **AppImage** - Universal Linux binary (no installation required)
- **RPM** - Linux package for Red Hat-based distributions
- **Future**: Windows installer, macOS app bundle

### For End Users - Download Options

1. **Python Source** - Use the installer (`python install.py`)
2. **Executable** - Download and run (no Python installation needed)
3. **AppImage** - Download, make executable, and run (Linux)
4. **RPM** - Install system-wide on Fedora/RHEL/CentOS

## 📄 License

This project is open source. See LICENSE file for details.

---

**Happy storytelling! 📚✨**