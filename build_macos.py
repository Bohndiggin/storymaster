#!/usr/bin/env python3
"""
macOS App Bundle Builder for Storymaster

Creates macOS .app bundles and .dmg installers from Linux.
Supports both native macOS builds and cross-compilation from Linux.

Cross-compilation requirements:
- osxcross toolchain (for compiling native extensions)
- PyInstaller with --target-arch support
- macOS SDK (legally obtained)
"""

import os
import sys
import shutil
import subprocess
import tempfile
import platform
from pathlib import Path


def print_header():
    """Print build header"""
    print("=" * 60)
    print("🍎 Storymaster macOS Builder")
    print("   macOS app bundle and DMG creation")
    print("=" * 60)
    print()


def check_cross_compilation_support():
    """Check if cross-compilation to macOS is possible"""
    print("📋 Checking macOS build capabilities...")
    
    is_macos = platform.system() == "Darwin"
    
    if is_macos:
        print("✅ Running on macOS - native build supported")
        return "native"
    
    # Check for osxcross toolchain
    osxcross_paths = [
        "/opt/osxcross",
        "/usr/local/osxcross",
        os.path.expanduser("~/osxcross")
    ]
    
    osxcross_found = False
    for path in osxcross_paths:
        if Path(path).exists():
            osxcross_found = True
            osxcross_root = path
            print(f"✅ osxcross found at {path}")
            break
    
    if not osxcross_found:
        print("⚠️  osxcross not found - cross-compilation not available")
        print("\n📖 To enable macOS cross-compilation from Linux:")
        print("   1. Install osxcross: https://github.com/tpoechtrager/osxcross")
        print("   2. Obtain macOS SDK (legally - from Xcode)")
        print("   3. Build osxcross toolchain")
        print("   4. Set environment variables")
        print("\n💡 Alternative: Use GitHub Actions or macOS VM for building")
        return None
    
    # Check for required environment variables
    required_env = ["OSXCROSS_ROOT", "OSXCROSS_HOST", "OSXCROSS_TARGET_DIR"]
    missing_env = []
    
    for var in required_env:
        if var not in os.environ:
            missing_env.append(var)
    
    if missing_env:
        print(f"⚠️  Missing environment variables: {', '.join(missing_env)}")
        print("\n🔧 Quick setup for osxcross:")
        print(f"   export OSXCROSS_ROOT={osxcross_root}")
        print("   export OSXCROSS_HOST=x86_64-apple-darwin20")
        print(f"   export OSXCROSS_TARGET_DIR={osxcross_root}/target")
        print(f"   export PATH={osxcross_root}/target/bin:$PATH")
        return None
    
    print("✅ Cross-compilation environment configured")
    return "cross"


def create_app_bundle_structure():
    """Create macOS .app bundle directory structure"""
    print("\n🏗️  Creating macOS app bundle structure...")
    
    app_name = "Storymaster.app"
    app_bundle = Path(app_name)
    
    # Clean up existing bundle
    if app_bundle.exists():
        shutil.rmtree(app_bundle)
    
    # Create bundle structure
    bundle_dirs = [
        "Contents",
        "Contents/MacOS",
        "Contents/Resources", 
        "Contents/Frameworks",
        "Contents/Resources/storymaster"
    ]
    
    for dir_path in bundle_dirs:
        (app_bundle / dir_path).mkdir(parents=True)
    
    print("✅ App bundle structure created")
    return app_bundle


def create_info_plist(app_bundle):
    """Create Info.plist for the app bundle"""
    print("📄 Creating Info.plist...")
    
    plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Storymaster</string>
    <key>CFBundleExecutable</key>
    <string>storymaster</string>
    <key>CFBundleIconFile</key>
    <string>storymaster.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.storymaster.app</string>
    <key>CFBundleName</key>
    <string>Storymaster</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>db</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>Storymaster Database</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
        </dict>
    </array>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>'''
    
    with open(app_bundle / "Contents/Info.plist", 'w') as f:
        f.write(plist_content)
    
    print("✅ Info.plist created")


def install_app_contents(app_bundle, build_mode):
    """Install application contents into the bundle"""
    print("\n📦 Installing application contents...")
    
    try:
        # Copy application files
        app_files = [
            'storymaster/',
            'tests/',
            'init_database.py', 
            'seed.py'
        ]
        
        # Add .env if it exists
        if Path('.env').exists():
            app_files.append('.env')
        
        resources_dir = app_bundle / "Contents/Resources/storymaster"
        
        for file_path in app_files:
            src = Path(file_path)
            if src.exists():
                dst = resources_dir / src.name
                if src.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"   Copied {file_path}")
            else:
                print(f"   Skipped {file_path} (not found)")
        
        # Create launcher script
        launcher_script = app_bundle / "Contents/MacOS/storymaster"
        launcher_content = '''#!/bin/bash
# Storymaster macOS launcher

# Get the bundle directory
BUNDLE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESOURCES_DIR="$BUNDLE_DIR/Resources/storymaster"

# Set up environment
export PYTHONPATH="$RESOURCES_DIR:$PYTHONPATH"

# Load .env file if it exists
if [ -f "$RESOURCES_DIR/.env" ]; then
    export $(grep -v '^#' "$RESOURCES_DIR/.env" | xargs)
fi

# Use system Python3 (bundled Python would go in Frameworks/)
PYTHON_CMD="python3"

# Check Python availability
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python 3 is required but not installed. Please install Python 3.8 or newer from python.org and try again." buttons {"OK"} default button "OK"'
    exit 1
fi

# Set up user data directory
USER_DATA_DIR="$HOME/Library/Application Support/Storymaster"
mkdir -p "$USER_DATA_DIR"

# Initialize database if needed
if [ ! -f "$USER_DATA_DIR/storymaster.db" ]; then
    export DATABASE_CONNECTION="sqlite:///$USER_DATA_DIR/storymaster.db"
    export TEST_DATABASE_CONNECTION="sqlite:///$USER_DATA_DIR/test_storymaster.db"
    
    cd "$RESOURCES_DIR"
    $PYTHON_CMD init_database.py
    
    # Ask about sample data using native dialog
    response=$(osascript -e 'display dialog "Would you like to load sample story data?" buttons {"No", "Yes"} default button "Yes"')
    if [[ "$response" == *"Yes"* ]]; then
        $PYTHON_CMD seed.py
    fi
else
    export DATABASE_CONNECTION="sqlite:///$USER_DATA_DIR/storymaster.db"
    export TEST_DATABASE_CONNECTION="sqlite:///$USER_DATA_DIR/test_storymaster.db"
fi

# Launch the application
cd "$RESOURCES_DIR"
exec $PYTHON_CMD storymaster/main.py "$@"
'''
        
        with open(launcher_script, 'w') as f:
            f.write(launcher_content)
        
        os.chmod(launcher_script, 0o755)
        
        # Note: Icon creation would require iconutil (macOS) or external tools
        # For production builds, create a proper .icns file and place it in Resources/
        
        print("✅ Application contents installed")
        print("⚠️  Note: Icon creation requires iconutil (macOS) or external tools")
        return True
        
    except Exception as e:
        print(f"❌ Failed to install app contents: {e}")
        return False


def create_with_pyinstaller(build_mode):
    """Create macOS app using PyInstaller"""
    print("\n🔨 Building with PyInstaller...")
    
    try:
        # PyInstaller command for macOS
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--onedir",  # Create a directory instead of single file
            "--windowed",  # No console window
            "--name", "storymaster",
            "--add-data", "tests/model/database/test_data:tests/model/database/test_data",
            "--add-data", ".env:.",
            "--hidden-import", "PyQt6.QtCore",
            "--hidden-import", "PyQt6.QtGui", 
            "--hidden-import", "PyQt6.QtWidgets",
            "--hidden-import", "sqlalchemy.dialects.sqlite",
        ]
        
        # Add cross-compilation flags if building from Linux
        if build_mode == "cross":
            cmd.extend([
                "--target-arch", "x86_64",
                "--osx-bundle-identifier", "com.storymaster.app",
                # Note: This requires PyInstaller 5.0+ and proper osxcross setup
            ])
        
        cmd.append("storymaster/main.py")
        
        print(f"   Running: {' '.join(cmd)}")
        
        # Set environment for cross-compilation
        env = os.environ.copy()
        if build_mode == "cross":
            # Use environment variables from osxcross setup
            osxcross_host = env.get("OSXCROSS_HOST", "x86_64-apple-darwin20")
            env.update({
                "CC": f"{osxcross_host}-clang",
                "CXX": f"{osxcross_host}-clang++",
                "AR": f"{osxcross_host}-ar",
                "RANLIB": f"{osxcross_host}-ranlib",
            })
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyInstaller build completed")
            
            # PyInstaller creates dist/storymaster/ - convert to .app bundle
            dist_dir = Path("dist/storymaster")
            if dist_dir.exists():
                # Create proper .app bundle from PyInstaller output
                app_bundle = create_app_bundle_from_dist(dist_dir)
                if app_bundle:
                    print(f"✅ App bundle created: {app_bundle}")
                    return True
                else:
                    print("❌ Failed to create app bundle")
                    return False
            else:
                print("❌ Build artifacts not found")
                return False
        else:
            print(f"❌ PyInstaller failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ PyInstaller build failed: {e}")
        return False


def create_app_bundle_from_dist(dist_dir):
    """Convert PyInstaller dist directory to proper .app bundle"""
    print("📦 Converting PyInstaller output to .app bundle...")
    
    try:
        app_bundle = create_app_bundle_structure()
        
        # Copy PyInstaller contents to MacOS directory
        macos_dir = app_bundle / "Contents/MacOS"
        for item in dist_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, macos_dir / item.name)
            else:
                shutil.copy2(item, macos_dir / item.name)
        
        # Make the main executable actually executable
        main_exec = macos_dir / "storymaster"
        if main_exec.exists():
            os.chmod(main_exec, 0o755)
        
        # Create Info.plist
        create_info_plist(app_bundle)
        
        print("✅ App bundle conversion completed")
        return app_bundle
        
    except Exception as e:
        print(f"❌ Failed to convert to app bundle: {e}")
        return None


def create_dmg_installer(app_bundle):
    """Create a DMG installer (requires macOS or additional tools)"""
    print("\n💿 Creating DMG installer...")
    
    if platform.system() != "Darwin":
        print("⚠️  DMG creation requires macOS or cross-compilation tools")
        print("💡 Alternatives for Linux:")
        print("   • Use genisoimage to create ISO")
        print("   • Use dmg2img/dmg2iso tools")
        print("   • Package as tar.gz for macOS users")
        
        # Create a simple tar.gz instead
        try:
            subprocess.run([
                "tar", "czf", "Storymaster-macOS.tar.gz", 
                str(app_bundle)
            ], check=True)
            print("✅ Created Storymaster-macOS.tar.gz instead")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to create archive")
            return False
    
    # Native macOS DMG creation
    try:
        dmg_name = "Storymaster-macOS.dmg"
        
        # Create temporary DMG
        subprocess.run([
            "hdiutil", "create", "-srcfolder", str(app_bundle),
            "-volname", "Storymaster", dmg_name
        ], check=True)
        
        print(f"✅ DMG created: {dmg_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ DMG creation failed: {e}")
        return False


def create_installation_instructions():
    """Create installation instructions for macOS"""
    instructions = """# Storymaster for macOS

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
- PyQt6 (usually auto-installed)

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
pip3 install PyQt6 SQLAlchemy python-dotenv
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
"""
    
    with open("MACOS_INSTALL.md", "w") as f:
        f.write(instructions)
    
    print("✅ Installation instructions created: MACOS_INSTALL.md")


def print_completion_info(build_mode):
    """Print build completion information"""
    print("\n" + "=" * 60)
    print("🍎 macOS Build Complete!")
    print("=" * 60)
    print()
    
    if build_mode == "native":
        print("📁 Files created:")
        print("   • Storymaster.app - macOS application bundle")
        print("   • Storymaster-macOS.dmg - Installer disk image")
    elif build_mode == "cross":
        print("📁 Files created:")
        print("   • Storymaster.app - macOS application bundle")
        print("   • Storymaster-macOS.tar.gz - Archive for distribution")
    
    print()
    print("🚀 To distribute:")
    print("   1. Test on actual macOS systems")
    print("   2. Consider code signing for easier installation")
    print("   3. Upload to distribution platform")
    
    print()
    print("📋 macOS Distribution Notes:")
    print("   • Code signing recommended for easier installation")
    print("   • Notarization required for macOS 10.15+")
    print("   • Users may need to right-click → Open first time")
    print("   • Consider Mac App Store distribution")
    print("=" * 60)


def main():
    """Main build process"""
    import sys
    
    print_header()
    
    # Check for non-interactive mode (CI/CD)
    non_interactive = len(sys.argv) > 1 and sys.argv[1] == "--non-interactive"
    
    # Check build capabilities
    build_mode = check_cross_compilation_support()
    if not build_mode:
        if non_interactive:
            # In CI/CD, try the fallback test bundle
            print("\n🧪 Non-interactive mode: Creating test app bundle...")
            app_bundle = create_app_bundle_structure()
            create_info_plist(app_bundle)
            if install_app_contents(app_bundle, "test"):
                create_dmg_installer(app_bundle)
                create_installation_instructions()
                print("\n✅ Test app bundle created (requires manual Python setup)")
                return True
            return False
        
        print("\n💡 Alternatives for macOS distribution:")
        print("   • Use GitHub Actions with macOS runner")
        print("   • Use macOS virtual machine")
        print("   • Ask macOS users to build from source")
        print("   • Use cloud build services")
        
        # Offer fallback for testing/development
        print("\n🔧 Development options:")
        print("   1. Test app bundle creation (without PyInstaller)")
        print("   2. Exit")
        
        try:
            choice = input("Select option (1 or 2): ").strip()
            if choice == "1":
                print("\n🧪 Testing app bundle creation...")
                app_bundle = create_app_bundle_structure()
                create_info_plist(app_bundle)
                if install_app_contents(app_bundle, "test"):
                    create_dmg_installer(app_bundle)
                    create_installation_instructions()
                    print("\n✅ Test app bundle created (requires manual Python setup)")
                    return True
        except KeyboardInterrupt:
            print("\n❌ Build cancelled")
        
        return False
    
    # Choose build method
    print(f"\n🔧 Build mode: {build_mode}")
    
    if non_interactive:
        # In CI/CD, use PyInstaller by default
        choice = "1"
        print("Non-interactive mode: Using PyInstaller (recommended)")
    else:
        print("\nChoose build method:")
        print("   1. PyInstaller (recommended)")
        print("   2. Manual app bundle")
        
        try:
            choice = input("Select method (1 or 2): ").strip()
        except KeyboardInterrupt:
            print("\n❌ Build cancelled")
            return False
    
    success = False
    
    if choice == "1":
        success = create_with_pyinstaller(build_mode)
    elif choice == "2":
        app_bundle = create_app_bundle_structure()
        create_info_plist(app_bundle)
        if install_app_contents(app_bundle, build_mode):
            success = create_dmg_installer(app_bundle)
    else:
        print("❌ Invalid choice")
        return False
    
    if success:
        create_installation_instructions()
        print_completion_info(build_mode)
    
    return success


if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during build: {e}")
        sys.exit(1)