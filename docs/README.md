# 🏰 Storymaster

**Visual Story Plotting & World-Building Tool for Creative Writers**

![GitHub](https://img.shields.io/github/license/Bohndiggin/storymaster)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

Storymaster is a comprehensive PyQt6-based creative writing application that seamlessly combines visual story structure planning with detailed world-building capabilities. Perfect for novelists, screenwriters, and game designers who need to organize complex narratives and rich fictional worlds.

## ✨ Key Features

### 📈 Litographer - Visual Story Plotting
- **Interactive node-based interface** for plotting story beats with drag-and-drop functionality
- **Multiple plot support** - manage main plots, subplots, and character arcs simultaneously
- **Tension mapping** with visual flow indicators (Rising, Flat, Point, Lower)
- **Customizable node shapes** - rectangles, circles, diamonds, stars, hexagons, triangles
- **Linked-list navigation** for easy story flow management
- **Integrated scene notes** and beat descriptions

### 🎭 Character Arcs
- **Individual character development tracking** with dedicated arc management
- **Arc point system** for plotting character growth and transformation
- **Character-to-node connections** linking story beats to character development
- **Arc type customization** for different character journey patterns

### 🌍 Lorekeeper - World Building Database
- **Character management** - detailed actor profiles with relationships, backgrounds, classes, and races
- **Faction system** - complex organizational structures with hierarchies and conflicts
- **Location catalog** - comprehensive setting database with descriptions and connections
- **Historical timeline** - track events with multi-entity involvement
- **Object repository** - manage items, artifacts, and world elements
- **Dynamic relationship mapping** between all entities

### 🛠️ Technical Excellence
- **SQLite backend** - completely offline, portable, and backup-friendly
- **MVC architecture** - clean separation of concerns with SQLAlchemy ORM
- **Multi-user support** - user accounts with complete data isolation
- **Project isolation** - multiple stories/worlds in organized workspaces
- **Professional dark theme** - eye-friendly interface for long writing sessions
- **Cross-platform compatibility** - Windows, macOS, and Linux support

## 🚀 Quick Start

### 🌟 Instant Installation (Recommended)
**The fastest way to get started - no setup required!**

```bash
# Install and run with uvx (Python 3.8+ required)
uvx run git+https://github.com/Bohndiggin/storymaster.git

# Alternative: Install with pip
pip install git+https://github.com/Bohndiggin/storymaster.git
storymaster
```

*This method automatically handles dependencies, database setup, and launches the application!*

### 🔧 Development Installation

For contributors and developers who want to modify the code:

```bash
git clone https://github.com/Bohndiggin/storymaster.git
cd storymaster

# Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py

# Load sample data (optional)
python scripts/seed.py

# Start Storymaster
python storymaster/main.py
```

### 💻 Windows Executable
**Download ready-to-run executable from our releases:**
- No Python installation required
- All dependencies included
- Just download, extract, and run `storymaster.exe`
- Available in [GitHub Releases](https://github.com/Bohndiggin/storymaster/releases)

### 🐧 Linux AppImage
**Portable application for all Linux distributions:**
- Download the `.AppImage` file from releases
- Make executable: `chmod +x Storymaster-x86_64.AppImage`
- Run directly: `./Storymaster-x86_64.AppImage`
- Works on any Linux distribution without installation

## 📁 Architecture

```
storymaster/
├── storymaster/
│   ├── model/              # Data layer
│   │   ├── database/       # SQLAlchemy models and schema
│   │   ├── common/         # Shared model components
│   │   ├── litographer/    # Story plotting data models
│   │   └── lorekeeper/     # World-building data models
│   ├── view/               # UI components (PyQt6)
│   │   ├── common/         # Shared UI elements & user management
│   │   ├── litographer/    # Story plotting interface
│   │   ├── lorekeeper/     # World-building interface
│   │   └── character_arcs/ # Character development interface
│   ├── controller/         # Business logic
│   │   └── common/         # Shared controllers & user management
│   └── main.py            # Application entry point
├── tests/                  # Comprehensive test suite
│   ├── model/             # Database and logic tests
│   │   ├── database/      # Schema and test data
│   │   ├── litographer/   # Story plotting tests
│   │   └── lorekeeper/    # World-building tests
│   └── fixtures/          # Test utilities and data
├── assets/                 # Application assets
│   ├── storymaster_icon.ico    # Windows executable icon
│   ├── storymaster_icon.svg    # Vector icon (cross-platform)
│   └── storymaster_icon_*.png  # Various sizes for system integration
├── scripts/                # Build and utility scripts
│   ├── build_executable.py        # Cross-platform executable builder
│   ├── build_standalone.py        # Standalone executable builder (recommended)
│   ├── build_fast.py              # Fast development build
│   ├── build_appimage.py          # Linux AppImage builder
│   ├── build_rpm.py              # Linux RPM package builder
│   ├── build_macos.py            # macOS app bundle builder
│   ├── run_tests.py              # Lightweight test runner
│   ├── run_comprehensive_tests.py # Comprehensive test suite with coverage
│   ├── init_database.py          # Database initialization
│   ├── migrate_database.py       # Database migration tool
│   └── seed.py                  # Sample data loader
├── storymaster.spec          # PyInstaller configuration
├── storymaster.spec.rpm      # RPM package specification
└── requirements.txt         # Python dependencies
```

## 🎮 Using Storymaster

### Story Plotting Workflow
1. **Create Project** - Start with a new story workspace
2. **Add Plots** - Create main plot and subplots using the Plot menu
3. **Build Structure** - Add story nodes with custom shapes and connections
4. **Organize Sections** - Group scenes into acts or chapters
5. **Add Details** - Include notes, tension levels, and scene descriptions

### World Building Workflow
1. **Design Characters** - Create actors with detailed backgrounds
2. **Build Locations** - Establish settings with rich descriptions
3. **Create Factions** - Define organizations and their relationships
4. **Track History** - Record significant events and timelines
5. **Manage Objects** - Catalog important items and artifacts

### Plot Management
Access via the **Plot** menu:
- **New Plot** - Create additional storylines or character arcs
- **Switch Plot** - Navigate between different plot threads
- **Delete Plot** - Remove unused or completed plots
- **Open Project** - Switch between different story worlds

### User Management
Access via the **User** menu:
- **New User** - Create additional user accounts for multi-user environments
- **Switch User** - Change active user without restarting the application
- **Manage Users** - Add, switch, or delete user accounts
- **Data Isolation** - Each user maintains separate stories, settings, and data

## 🧪 Development

### Manual Development Setup
```bash
# Clone repository
git clone https://github.com/Bohndiggin/storymaster.git
cd storymaster

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py

# Load sample data
python scripts/seed.py

# Run application
python storymaster/main.py
```

### Testing
```bash
# Run all tests
python scripts/run_tests.py

# Run pytest tests
pytest tests/ -v

# Run specific test modules
pytest tests/model/litographer/ -v
pytest tests/controller/litographer/ -v

# Run comprehensive tests with coverage
python scripts/run_comprehensive_tests.py
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Type checking (if mypy is installed)
mypy storymaster/
```

### Database Management
```bash
# Initialize database
python scripts/init_database.py

# Load sample data
python scripts/seed.py

# Handle schema updates
python scripts/migrate_database.py
```

## 📦 Distribution & Building

Storymaster provides multiple distribution options for different platforms and use cases:

### Executable Builds
```bash
# Standalone executables (recommended for distribution)
python scripts/build_standalone.py

# Traditional PyInstaller build
python scripts/build_executable.py

# Linux AppImage
python scripts/build_appimage.py

# Fast development build
python scripts/build_fast.py

# Platform-specific builds
python scripts/build_rpm.py         # Linux RPM packages  
python scripts/build_macos.py       # macOS app bundles
```

### Distribution Features
- **Windows**: Standalone `.exe` with all dependencies
- **Linux AppImage**: Universal binary that runs on any distribution
- **Linux RPM**: Native packages for Red Hat-based systems
- **macOS**: Native `.app` bundles with installer DMG
- **Cross-platform**: Portable executables for development/testing

### Icon Assets
All build systems use proper icons from the `assets/` directory:
- `storymaster_icon.ico` - Windows executables
- `storymaster_icon.svg` - Cross-platform vector icon
- `storymaster_icon_*.png` - Various sizes for system integration

## 🗄️ Data Management

### Database Features
- **SQLite backend** - Single file database (`storymaster.db`)
- **Portable storage** - Copy `.db` file to backup entire project
- **Offline operation** - No internet connection required
- **Relational integrity** - Foreign key constraints and data validation
- **Sample data included** - Example characters, locations, and story structure

### Backup Strategy
Simply copy `storymaster.db` to preserve all your work:
```bash
cp storymaster.db backup/storymaster_backup_$(date +%Y%m%d).db
```

## 🔧 Troubleshooting

### Common Issues

**Environment Problems:**
- `ModuleNotFoundError` → Ensure virtual environment is activated
- `Database connection failed` → Run `python scripts/init_database.py`
- `PyQt6 import error` → Reinstall with `pip install PyQt6`

**Database Issues:**
- Corrupt database → Delete `storymaster.db` and run `init_database.py`
- Missing tables → Run `python scripts/init_database.py` to recreate schema
- Performance issues → Consider archiving old projects

**UI Problems:**
- Blank interface → Check console for PyQt6 errors
- Node positioning issues → Clear cache and restart application
- Menu not responding → Verify database connection

### Getting Support
- 📖 Check [CLAUDE.md](./CLAUDE.md) for detailed technical documentation
- 🐛 Report bugs at [GitHub Issues](https://github.com/Bohndiggin/storymaster/issues)
- 💡 Request features via GitHub Issues with the "enhancement" label
- 📝 Review sample data to understand the data model

## 🌟 Contributing

We welcome contributions! Please see our development workflow:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow existing code style (Black formatting)
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the user interface
- Database powered by [SQLAlchemy](https://www.sqlalchemy.org/) ORM
- Inspired by professional story development tools and writing methodologies

---

**Start crafting your next great story today! 📚✨**

*For detailed technical documentation, see [CLAUDE.md](./CLAUDE.md)*