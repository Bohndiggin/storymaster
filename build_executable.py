#!/usr/bin/env python3
"""
Build script for creating Storymaster executables

This script builds cross-platform executables using PyInstaller.
Supports Windows (.exe), Linux, and macOS executables.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def print_header():
    """Print build header"""
    print("=" * 60)
    print("Storymaster Executable Builder")
    print("Cross-platform executable creation")
    print("=" * 60)
    print()


def check_dependencies():
    """Check if PyInstaller is available"""
    print("Checking build dependencies...")

    try:
        import PyInstaller

        print(f"PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller==6.11.1"],
                check=True,
            )
            print("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller")
            return False


def ensure_icons_exist():
    """Ensure icon files exist for the build"""
    print("Checking for icon files...")
    icon_path = Path("assets/storymaster_icon.ico")
    if not icon_path.exists():
        print("Warning: Icon assets not found at assets/storymaster_icon.ico")
        print("The build will continue but the executable may not have an icon")
        print("To add icons, ensure the assets/ directory contains:")
        print("  - storymaster_icon.ico (Windows)")
        print("  - storymaster_icon.svg (cross-platform)")
        print("  - storymaster_icon_*.png (various sizes)")
    else:
        print("Using icon from assets: assets/storymaster_icon.ico")
    return True


def clean_previous_builds():
    """Clean up previous build artifacts"""
    print("\n[CLEAN] Cleaning previous builds...")

    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.pyc"]

    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")

    # Clean pyc files recursively
    for pyc_file in Path(".").rglob("*.pyc"):
        pyc_file.unlink()

    for pycache_dir in Path(".").rglob("__pycache__"):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)

    print("[OK] Build cleanup complete")
    return True


def build_executable():
    """Build the executable using PyInstaller"""
    print("\n[COMPILE] Building executable...")

    try:
        # Run PyInstaller with our spec file
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "storymaster.spec"]

        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("[OK] Executable built successfully!")
            return True
        else:
            print(f"[ERROR] Build failed: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] PyInstaller failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def create_portable_package():
    """Create a portable package with database and sample data"""
    print("\n[PACKAGE] Creating portable package...")

    # For one-file build, executable is directly in dist/
    system = platform.system().lower()
    if system == "windows":
        exe_path = Path("dist/storymaster.exe")
    else:
        exe_path = Path("dist/storymaster")
        
    if not exe_path.exists():
        print(f"[ERROR] Executable not found at {exe_path}")
        return False
        
    # Create distribution directory
    dist_dir = Path("dist/storymaster_portable")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)

    try:
        # Copy the executable to the portable directory
        if system == "windows":
            shutil.copy2(exe_path, dist_dir / "storymaster.exe")
            print("   Copied Windows executable")
        else:
            shutil.copy2(exe_path, dist_dir / "storymaster")
            os.chmod(dist_dir / "storymaster", 0o755)
            print("   Copied Linux executable")

        # Copy database if it exists
        if Path("storymaster.db").exists():
            shutil.copy2("storymaster.db", dist_dir / "storymaster.db")
            print("   Copied sample database")

        # Create a README for the portable package
        readme_content = f"""# Storymaster Portable

This is a standalone version of Storymaster that runs without installation.
**No Python or PyQt6 installation required!**

## How to Run

### Windows:
Double-click `storymaster.exe`

### Linux:
Open terminal in this directory and run:
```bash
./storymaster
```

## Features

✅ **Fully Standalone**: No dependencies required
✅ **Python Runtime**: Bundled Python {platform.python_version()}
✅ **PyQt6 GUI**: Complete UI framework included
✅ **SQLAlchemy**: Database layer bundled
✅ **Cross-Platform**: Same features on Windows and Linux

## Database

The `storymaster.db` file contains your story data. 
To backup your work, simply copy this file.

## First Time Setup

If no database exists, the application will create an empty one.
You can seed it with sample data using the application's built-in functionality.

## Performance Notes

- First startup may take 10-15 seconds (extracting bundled files)
- Subsequent startups are much faster
- The executable is self-contained and portable

## File Sizes

- Windows: ~150MB (includes full Python + PyQt6)
- Linux: ~120MB (leverages some system libraries)

## Troubleshooting

### Windows:
- If Windows Defender blocks it, allow the application
- Run as Administrator if database creation fails
- Check Windows Event Viewer for detailed error logs

### Linux:
- Ensure execute permissions: `chmod +x storymaster`
- Install basic graphics libraries if needed:
  ```bash
  # Ubuntu/Debian:
  sudo apt install libxcb-xinerama0 libxcb-cursor0
  
  # Fedora/RHEL:
  sudo dnf install xcb-util-cursor
  ```
- Try running from terminal to see error messages

## Benefits of Standalone Build

- ✅ No Python installation required
- ✅ No dependency conflicts
- ✅ Consistent behavior across systems
- ✅ Easy to distribute and deploy
- ✅ Self-contained and portable
- ✅ Works on clean systems

For more help, visit: https://github.com/your-repo/storymaster
"""

        with open(dist_dir / "README.txt", "w") as f:
            f.write(readme_content)

        print("[OK] Portable package created in dist/storymaster_portable/")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to create portable package: {e}")
        return False


def create_archive():
    """Create a compressed archive of the executable"""
    print("\n[FILES] Creating distribution archive...")

    system = platform.system().lower()
    arch = platform.machine().lower()

    # Define archive name
    archive_name = f"storymaster-standalone-{system}-{arch}"

    dist_dir = Path("dist")
    portable_dir = dist_dir / "storymaster_portable"
    if not portable_dir.exists():
        print("[ERROR] No portable package found to archive")
        return False

    try:
        # Create archive based on platform
        if system == "windows":
            archive_path = f"{archive_name}.zip"
            shutil.make_archive(archive_name, "zip", dist_dir, "storymaster_portable")
        else:
            archive_path = f"{archive_name}.tar.gz"
            shutil.make_archive(archive_name, "gztar", dist_dir, "storymaster_portable")

        print(f"[OK] Archive created: {archive_path}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to create archive: {e}")
        return False


def print_completion_info():
    """Print build completion information"""
    system = platform.system()
    arch = platform.machine()

    print("\n" + "=" * 60)
    print("[SUCCESS] Build Complete!")
    print("=" * 60)
    print()
    print("[FILES] Files created:")
    print(
        f"   • Executable: dist/storymaster/storymaster{'.exe' if system == 'Windows' else ''}"
    )
    print(
        f"   • Archive: storymaster-{system.lower()}-{arch.lower()}.{'zip' if system == 'Windows' else 'tar.gz'}"
    )
    print()
    print("[DEPLOY] To distribute:")
    print("   1. Share the archive file")
    print("   2. Users extract and run the executable")
    print("   3. No Python installation required!")
    print()
    print("[NOTE] Note: The executable includes:")
    print("   • Complete Python runtime")
    print("   • All dependencies (PyQt6, SQLAlchemy)")
    print("   • Sample database and test data")
    print("   • UI files and resources")
    print("=" * 60)


def main():
    """Main build process"""
    print_header()

    # Build steps
    steps = [
        ("Checking dependencies", check_dependencies),
        ("Ensuring icons exist", ensure_icons_exist),
        ("Cleaning previous builds", clean_previous_builds),
        ("Building executable", build_executable),
        ("Creating portable package", create_portable_package),
        ("Creating distribution archive", create_archive),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n[ERROR] Build failed at: {step_name}")
            sys.exit(1)

    print_completion_info()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING]  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during build: {e}")
        sys.exit(1)
