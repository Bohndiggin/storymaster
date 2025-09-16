# Storymaster for macOS

## Installation Options

### Option 1: App Bundle (.app)
1. Download `Storymaster.app`
2. Drag to Applications folder
3. Right-click and select "Open" (first time only, due to Gatekeeper)
4. Grant permissions if prompted

### Option 2: Archive (.tar.gz)
1. Download `Storymaster-macOS.tar.gz`
2. Double-click to extract
3. Drag `Storymaster.app` to Applications
4. Right-click and "Open" first time

## Requirements

- macOS 10.14 (Mojave) or later
- Python 3.8 or newer (install from python.org if needed)
- PySide6 (usually auto-installed)

## First Run

On first launch, Storymaster will:
1. Create a database in `~/Library/Application Support/Storymaster/`
2. Ask if you want to load sample data
3. Launch the application

## Permissions

Storymaster may request permissions for:
- File system access (to save your stories)
- Network access (for future online features)

## Troubleshooting

### "App is damaged" or won't open:
```bash
# Remove quarantine attribute
xattr -cr /Applications/Storymaster.app
```

### Python not found:
1. Install Python from https://python.org
2. Or install via Homebrew: `brew install python3`

### Dependencies missing:
```bash
pip3 install PySide6 SQLAlchemy
```

## Uninstalling

1. Move `Storymaster.app` to Trash
2. Remove user data: `~/Library/Application Support/Storymaster/`

## Building from Source

On macOS, you can build locally:
```bash
python build_macos.py
```

This creates a native .app bundle and .dmg installer.
