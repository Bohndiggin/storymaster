#!/usr/bin/env python3
"""
Build script for creating Storymaster executables

This script builds cross-platform executables using PyInstaller.
Supports Windows (.exe), Linux, and macOS executables.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def print_header():
    """Print build header"""
    print("=" * 60)
    print("🏗️  Storymaster Executable Builder")
    print("   Cross-platform executable creation")
    print("=" * 60)
    print()


def check_dependencies():
    """Check if PyInstaller is available"""
    print("📋 Checking build dependencies...")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller==6.11.1"], check=True)
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False


def clean_previous_builds():
    """Clean up previous build artifacts"""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean pyc files recursively
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
    
    for pycache_dir in Path('.').rglob('__pycache__'):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)
    
    print("✅ Build cleanup complete")


def build_executable():
    """Build the executable using PyInstaller"""
    print("\n🔨 Building executable...")
    
    try:
        # Run PyInstaller with our spec file
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "storymaster.spec"]
        
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully!")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def create_portable_package():
    """Create a portable package with database and sample data"""
    print("\n📦 Creating portable package...")
    
    dist_dir = Path("dist/storymaster")
    if not dist_dir.exists():
        print("❌ Executable not found in dist/storymaster")
        return False
    
    try:
        # Create empty database in the dist directory
        print("   Initializing database...")
        
        # Change to dist directory and run database init
        original_dir = os.getcwd()
        os.chdir(dist_dir)
        
        # Run the executable to create database (if init_database.py is bundled)
        # For now, we'll copy the database from the main directory
        os.chdir(original_dir)
        
        # Copy database if it exists
        if Path("storymaster.db").exists():
            shutil.copy2("storymaster.db", dist_dir / "storymaster.db")
            print("   Copied sample database")
        
        # Create a README for the portable package
        readme_content = """# Storymaster Portable

This is a portable version of Storymaster that runs without installation.

## How to Run

### Windows:
Double-click `storymaster.exe`

### Linux/macOS:
Open terminal in this directory and run:
./storymaster

## Database

The `storymaster.db` file contains your story data. 
To backup your work, simply copy this file.

## First Time Setup

If no database exists, the application will create an empty one.
You can seed it with sample data by running the seed functionality
from within the application.

## Troubleshooting

If the application doesn't start:
1. Make sure you have the necessary system libraries
2. Check that the database file is writable
3. Try running from a terminal to see error messages

For more help, visit: https://github.com/your-repo/storymaster
"""
        
        with open(dist_dir / "README.txt", "w") as f:
            f.write(readme_content)
        
        print("✅ Portable package created in dist/storymaster/")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create portable package: {e}")
        return False


def create_archive():
    """Create a compressed archive of the executable"""
    print("\n📁 Creating distribution archive...")
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Define archive name
    archive_name = f"storymaster-{system}-{arch}"
    
    dist_dir = Path("dist")
    if not (dist_dir / "storymaster").exists():
        print("❌ No build found to archive")
        return False
    
    try:
        # Create archive based on platform
        if system == "windows":
            archive_path = f"{archive_name}.zip"
            shutil.make_archive(archive_name, 'zip', dist_dir, 'storymaster')
        else:
            archive_path = f"{archive_name}.tar.gz"
            shutil.make_archive(archive_name, 'gztar', dist_dir, 'storymaster')
        
        print(f"✅ Archive created: {archive_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create archive: {e}")
        return False


def print_completion_info():
    """Print build completion information"""
    system = platform.system()
    arch = platform.machine()
    archive = 'zip' if system == 'Windows' else 'tar.gz'
    extension = '.exe' if system == 'Windows' else ''
    print("\n" + "=" * 60)
    print("🎉 Build Complete!")
    print("=" * 60)
    print()
    print("📁 Files created:")
    print(f"   • Executable: dist/storymaster/storymaster{extension}")
    print(f"   • Archive: storymaster-{system.lower()}-{arch.lower()}.{archive}")
    print()
    print("🚀 To distribute:")
    print("   1. Share the archive file")
    print("   2. Users extract and run the executable")
    print("   3. No Python installation required!")
    print()
    print("📝 Note: The executable includes:")
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
        ("Cleaning previous builds", clean_previous_builds),
        ("Building executable", build_executable),
        ("Creating portable package", create_portable_package),
        ("Creating distribution archive", create_archive)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Build failed at: {step_name}")
            sys.exit(1)
    
    print_completion_info()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during build: {e}")
        sys.exit(1)