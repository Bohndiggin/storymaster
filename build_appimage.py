#!/usr/bin/env python3
"""
AppImage Builder for Storymaster

Creates a universal Linux binary that runs on any distribution
without installation. AppImages are portable and self-contained.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


def print_header():
    """Print build header"""
    print("=" * 60)
    print("[MOBILE] Storymaster AppImage Builder")
    print("   Universal Linux binary creation")
    print("=" * 60)
    print()


def download_appimage_tool():
    """Download appimagetool if not present"""
    print("[CHECK] Checking AppImage tools...")

    tool_path = Path("appimagetool-x86_64.AppImage")

    if tool_path.exists():
        print("[OK] appimagetool found")
        return str(tool_path)

    print("[DOWNLOAD]  Downloading appimagetool...")

    try:
        url = "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
        urllib.request.urlretrieve(url, tool_path)

        # Make executable
        os.chmod(tool_path, 0o755)

        print("[OK] appimagetool downloaded")
        return str(tool_path)

    except Exception as e:
        print(f"[ERROR] Failed to download appimagetool: {e}")
        return None


def create_appdir_structure():
    """Create AppDir structure for AppImage"""
    print("\n[BUILD]  Creating AppDir structure...")

    appdir = Path("Storymaster.AppDir")

    # Clean up existing AppDir
    if appdir.exists():
        shutil.rmtree(appdir)

    # Create directory structure
    dirs = [
        "usr/bin",
        "usr/share/applications",
        "usr/share/icons/hicolor/scalable/apps",
        "usr/share/storymaster",
    ]

    for dir_path in dirs:
        (appdir / dir_path).mkdir(parents=True)

    print("[OK] AppDir structure created")
    return appdir


def install_python_app(appdir):
    """Install Python application and dependencies into AppDir"""
    print("\n[PACKAGE] Installing application into AppDir...")

    try:
        # Copy application files
        app_files = ["storymaster/", "tests/", "init_database.py"]

        for file_path in app_files:
            src = Path(file_path)
            if src.exists():
                dst = appdir / "usr/share/storymaster" / src.name
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"   Copied {file_path}")

        # Create virtual environment for bundled dependencies
        print("   Creating virtual environment for dependencies...")
        venv_path = appdir / "usr/share/storymaster/venv"
        subprocess.run(["python3", "-m", "venv", str(venv_path)], check=True)

        # Install dependencies in virtual environment
        pip_path = venv_path / "bin/pip"
        subprocess.run([str(pip_path), "install", "SQLAlchemy==2.0.41"], check=True)
        print("   Installed SQLAlchemy in virtual environment")

        # Create launcher script
        launcher_script = appdir / "usr/bin/storymaster"
        launcher_content = """#!/bin/bash
# Storymaster AppImage launcher

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/../share/storymaster"

# Set up environment
export APPDIR="${APPDIR:-$(dirname "$SCRIPT_DIR")}"
export PYTHONPATH="$APP_DIR:$PYTHONPATH"

# Smart Python selection: use system Python for PyQt6, bundled for SQLAlchemy
VENV_PYTHON="$APP_DIR/venv/bin/python"

# Check if system python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.8 or newer and try again."
    exit 1
fi

# Test if system Python has PyQt6 (preferred for GUI applications)
if python3 -c "import PyQt6" 2>/dev/null; then
    echo "Using system Python with PyQt6"
    PYTHON_CMD="python3"
    
    # Set PYTHONPATH to include bundled SQLAlchemy if available
    if [ -f "$VENV_PYTHON" ]; then
        VENV_SITE_PACKAGES=$(echo "$APP_DIR"/venv/lib/python*/site-packages)
        export PYTHONPATH="$VENV_SITE_PACKAGES:$PYTHONPATH"
        echo "Added bundled SQLAlchemy to Python path"
    else
        # Check if SQLAlchemy is available system-wide
        python3 -c "import sqlalchemy" 2>/dev/null || {
            echo "Error: SQLAlchemy is missing."
            echo "Please install: sudo apt install python3-sqlalchemy"
            echo "Or via pip: pip install SQLAlchemy"
            exit 1
        }
    fi
else
    echo "Error: PyQt6 is required but not found."
    echo "Please install PyQt6:"
    echo "  Ubuntu/Debian: sudo apt install python3-pyqt6"
    echo "  Fedora/RHEL:   sudo dnf install python3-PyQt6"
    echo "  Or via pip:    pip install PyQt6"
    exit 1
fi

# Change to app directory
cd "$APP_DIR"

# Initialize database if needed
if [ ! -f "$HOME/.local/share/storymaster/storymaster.db" ]; then
    mkdir -p "$HOME/.local/share/storymaster"
    
    echo "Initializing Storymaster database..."
    $PYTHON_CMD init_database.py
    
    echo "Would you like to load sample data? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        $PYTHON_CMD seed.py
    fi
fi

# Launch the application
exec $PYTHON_CMD storymaster/main.py "$@"
"""

        with open(launcher_script, "w") as f:
            f.write(launcher_content)

        os.chmod(launcher_script, 0o755)

        # Create desktop entry
        desktop_entry = appdir / "usr/share/applications/storymaster.desktop"
        desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Storymaster
Comment=Visual Story Plotting & World-Building Tool  
GenericName=Story Writing Tool
Exec=storymaster %F
Icon=storymaster
Terminal=false
Categories=Office;Publishing;Writing;
Keywords=writing;story;plot;worldbuilding;creative;novel;screenplay;
StartupNotify=true
MimeType=application/x-storymaster;
StartupWMClass=storymaster
"""

        with open(desktop_entry, "w") as f:
            f.write(desktop_content)

        # Use the proper icon from assets
        icon_path = appdir / "usr/share/icons/hicolor/scalable/apps/storymaster.svg"
        assets_icon_svg = Path("assets/storymaster_icon.svg")
        
        if assets_icon_svg.exists():
            # Copy the proper icon
            shutil.copy2(assets_icon_svg, icon_path)
            print(f"   Using icon from assets: {assets_icon_svg}")
        else:
            # Fallback to emoji icon if assets don't exist
            icon_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" fill="#1a1a1a" rx="8"/>
  <text x="32" y="44" text-anchor="middle" fill="#ffffff" font-size="32" font-family="Arial, sans-serif">🏰</text>
</svg>"""
            with open(icon_path, "w") as f:
                f.write(icon_content)
            print("   Using fallback emoji icon (run create_icons.py to generate proper icons)")

        # Copy icon and desktop file to AppDir root (required for AppImage)
        shutil.copy2(icon_path, appdir / "storymaster.svg")
        shutil.copy2(desktop_entry, appdir / "storymaster.desktop")

        # Create AppRun script
        apprun_script = appdir / "AppRun"
        apprun_content = """#!/bin/bash
# AppRun script for Storymaster

exec "$APPDIR/usr/bin/storymaster" "$@"
"""

        with open(apprun_script, "w") as f:
            f.write(apprun_content)

        os.chmod(apprun_script, 0o755)

        print("[OK] Application installed into AppDir")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to install application: {e}")
        return False


def build_appimage(appdir, appimagetool_path):
    """Build the AppImage using appimagetool"""
    print("\n[COMPILE] Building AppImage...")

    try:
        # Set environment variable to skip desktop integration
        env = os.environ.copy()
        env["ARCH"] = "x86_64"

        cmd = [f"./{appimagetool_path}", str(appdir), "Storymaster-x86_64.AppImage"]

        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode == 0:
            print("[OK] AppImage built successfully!")
            return "Storymaster-x86_64.AppImage"
        else:
            print(f"[ERROR] AppImage build failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to build AppImage: {e}")
        return None


def create_installation_instructions():
    """Create installation instructions for the AppImage"""
    instructions = """# Storymaster AppImage

## What is an AppImage?

An AppImage is a portable application format for Linux that:
- Runs on any Linux distribution
- Requires no installation or root privileges
- Includes all dependencies
- Can be run directly after download

## How to Use

1. **Download** the `Storymaster-x86_64.AppImage` file
2. **Make executable**:
   ```bash
   chmod +x Storymaster-x86_64.AppImage
   ```
3. **Run** the application:
   ```bash
   ./Storymaster-x86_64.AppImage
   ```

## Requirements

- Linux x86_64 system  
- Python 3.8 or newer (usually pre-installed)
- PyQt6 system libraries (auto-installed on most modern distributions)

**Note**: SQLAlchemy is bundled in the AppImage, no additional installation required!

## First Run

On first run, Storymaster will:
1. Create a database in `~/.local/share/storymaster/`
2. Ask if you want to load sample data
3. Launch the application

## Integration (Optional)

To add Storymaster to your system menu:
```bash
# Move to applications directory
mv Storymaster-x86_64.AppImage ~/.local/bin/
# or
sudo mv Storymaster-x86_64.AppImage /usr/local/bin/
```

Some file managers also support right-click → "Integrate" for AppImages.

## Updating

Simply download the new AppImage and replace the old one.

## Uninstalling

Delete the AppImage file. User data remains in `~/.local/share/storymaster/`.

## Troubleshooting

If the AppImage doesn't run:
1. Ensure it's executable: `chmod +x Storymaster-x86_64.AppImage`
2. Check Python 3 is installed: `python3 --version`
3. Install PyQt6 if needed:
   - Ubuntu/Debian: `sudo apt install python3-pyqt6`
   - Fedora/RHEL: `sudo dnf install python3-PyQt6`
   - Or via pip: `pip install PyQt6`
4. Try running from terminal to see error messages

**Note**: SQLAlchemy is bundled, so you only need PyQt6!

## Benefits of AppImage

- [OK] No installation required
- [OK] Works on any Linux distribution
- [OK] No root privileges needed
- [OK] No dependency conflicts
- [OK] Easy to distribute and update
- [OK] Sandboxed execution
"""

    with open("APPIMAGE_USAGE.md", "w") as f:
        f.write(instructions)

    print("[OK] Usage instructions created: APPIMAGE_USAGE.md")


def print_completion_info():
    """Print build completion information"""
    print("\n" + "=" * 60)
    print("[MOBILE] AppImage Build Complete!")
    print("=" * 60)
    print()
    print("[FILES] File created:")
    print("   • Storymaster-x86_64.AppImage")
    print()
    print("[DEPLOY] To distribute:")
    print("   1. Share the .AppImage file")
    print("   2. Users make it executable and run")
    print("   3. No installation required!")
    print()
    print("[FEATURE] AppImage benefits:")
    print("   • Universal Linux compatibility")
    print("   • No root privileges required")
    print("   • Portable - runs from any location")
    print("   • Self-contained with all dependencies")
    print("   • Easy updates - just replace the file")
    print("=" * 60)


def main():
    """Main build process"""
    print_header()

    # Check if we're on Linux
    if not sys.platform.startswith("linux"):
        print("[ERROR] AppImage building is only supported on Linux")
        return False

    # Download appimagetool
    appimagetool_path = download_appimage_tool()
    if not appimagetool_path:
        return False

    # Create AppDir structure
    appdir = create_appdir_structure()

    # Install application
    if not install_python_app(appdir):
        return False

    # Build AppImage
    appimage_file = build_appimage(appdir, appimagetool_path)
    if not appimage_file:
        return False

    # Create instructions
    create_installation_instructions()

    # Cleanup
    shutil.rmtree(appdir)
    print(f"\n[CLEAN] Cleaned up build directory")

    print_completion_info()
    return True


if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[WARNING]  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during build: {e}")
        sys.exit(1)
