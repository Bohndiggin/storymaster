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
- **Project isolation** - multiple stories/worlds in organized workspaces
- **Professional dark theme** - eye-friendly interface for long writing sessions
- **Cross-platform compatibility** - Windows, macOS, and Linux support

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git (for development)

### One-Command Installation
```bash
git clone https://github.com/Bohndiggin/storymaster.git
cd storymaster
python install.py
```

The installer automatically:
- ✅ Creates an isolated virtual environment
- ✅ Installs all required dependencies
- ✅ Initializes the SQLite database schema
- ✅ Optionally seeds with sample story data

### Launch Application
```bash
# Activate virtual environment
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows

# Start Storymaster
python storymaster/main.py
```

## 📁 Architecture

```
storymaster/
├── storymaster/
│   ├── model/              # Data layer
│   │   └── database/       # SQLAlchemy models and schema
│   ├── view/               # UI components (PyQt6)
│   │   ├── common/         # Shared UI elements
│   │   ├── litographer/    # Story plotting interface
│   │   └── lorekeeper/     # World-building interface
│   ├── controller/         # Business logic
│   │   ├── common/         # Shared controllers
│   │   ├── litographer/    # Plot management logic
│   │   └── lorekeeper/     # World-building logic
│   └── main.py            # Application entry point
├── tests/                  # Comprehensive test suite
│   ├── model/             # Database and logic tests
│   └── fixtures/          # Test data and utilities
├── install.py             # Automated installer
├── init_database.py       # Database initialization
├── seed.py               # Sample data loader
└── requirements.txt      # Python dependencies
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
python init_database.py

# Load sample data
python seed.py

# Run application
python storymaster/main.py
```

### Testing
```bash
# Run full test suite
pytest

# Run specific modules
pytest tests/model/litographer/
pytest tests/model/lorekeeper/

# Verbose output
pytest -v
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
# Reset database
python init_database.py

# Reload sample data
python seed.py
```

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
- `Database connection failed` → Run `python init_database.py`
- `PyQt6 import error` → Reinstall with `pip install PyQt6`

**Database Issues:**
- Corrupt database → Delete `storymaster.db` and run `init_database.py`
- Missing tables → Run `python init_database.py` to recreate schema
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