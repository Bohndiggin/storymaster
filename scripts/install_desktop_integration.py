#!/usr/bin/env python3
"""
Desktop Integration Installer for Storymaster
Installs desktop entry and icons for proper Linux integration
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_header():
    """Print installation header"""
    print("=" * 60)
    print("Storymaster Desktop Integration Installer")
    print("Installing desktop entry and icons for Linux")
    print("=" * 60)
    print()


def install_desktop_entry():
    """Install desktop entry"""
    print("[INSTALL] Installing desktop entry...")
    
    # Source desktop file
    desktop_source = Path("assets/storymaster.desktop")
    if not desktop_source.exists():
        print(f"[ERROR] Desktop file not found: {desktop_source}")
        return False
    
    # Destination directory
    apps_dir = Path.home() / ".local/share/applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy desktop file
    desktop_dest = apps_dir / "storymaster.desktop"
    shutil.copy2(desktop_source, desktop_dest)
    
    print(f"[OK] Desktop entry installed: {desktop_dest}")
    return True


def install_icons():
    """Install application icons"""
    print("[INSTALL] Installing application icons...")
    
    # Icon directory
    icons_dir = Path.home() / ".local/share/icons/hicolor"
    
    # Icon files to install
    icon_files = [
        ("assets/storymaster_icon_16.png", "16x16/apps/storymaster.png"),
        ("assets/storymaster_icon_32.png", "32x32/apps/storymaster.png"), 
        ("assets/storymaster_icon_64.png", "64x64/apps/storymaster.png"),
        ("assets/storymaster_icon.svg", "scalable/apps/storymaster.svg")
    ]
    
    installed_count = 0
    for source_path, dest_path in icon_files:
        source = Path(source_path)
        if source.exists():
            dest = icons_dir / dest_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            print(f"   ✓ Installed: {dest}")
            installed_count += 1
        else:
            print(f"   ✗ Missing: {source}")
    
    if installed_count > 0:
        print(f"[OK] Installed {installed_count} icon files")
        return True
    else:
        print("[ERROR] No icon files found to install")
        return False


def update_desktop_database():
    """Update desktop database"""
    print("[UPDATE] Updating desktop database...")
    
    apps_dir = Path.home() / ".local/share/applications"
    
    try:
        subprocess.run(
            ["update-desktop-database", str(apps_dir)],
            check=True,
            capture_output=True
        )
        print("[OK] Desktop database updated")
        return True
    except subprocess.CalledProcessError:
        print("[WARNING] Could not update desktop database")
        return True  # Not critical
    except FileNotFoundError:
        print("[WARNING] update-desktop-database not found")
        return True  # Not critical


def update_icon_cache():
    """Update icon cache"""
    print("[UPDATE] Updating icon cache...")
    
    icons_dir = Path.home() / ".local/share/icons"
    
    try:
        subprocess.run(
            ["gtk-update-icon-cache", str(icons_dir)],
            check=True,
            capture_output=True
        )
        print("[OK] Icon cache updated")
        return True
    except subprocess.CalledProcessError:
        print("[WARNING] Could not update icon cache")
        return True  # Not critical
    except FileNotFoundError:
        print("[WARNING] gtk-update-icon-cache not found")
        return True  # Not critical


def create_executable_link():
    """Create symbolic link to executable in PATH"""
    print("[LINK] Creating executable link...")
    
    # Find the built executable
    exe_path = None
    possible_paths = [
        Path("dist/storymaster"),
        Path("dist/storymaster_portable/storymaster")
    ]
    
    for path in possible_paths:
        if path.exists():
            exe_path = path.resolve()
            break
    
    if not exe_path:
        print("[WARNING] Executable not found, skipping link creation")
        return True  # Not critical
    
    # Create link in user's local bin
    bin_dir = Path.home() / ".local/bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    link_path = bin_dir / "storymaster"
    
    try:
        # Remove existing link
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        
        # Create new link
        link_path.symlink_to(exe_path)
        print(f"[OK] Executable linked: {link_path} -> {exe_path}")
        return True
    except Exception as e:
        print(f"[WARNING] Could not create executable link: {e}")
        return True  # Not critical


def print_completion_info():
    """Print completion information"""
    print("\n" + "=" * 60)
    print("[SUCCESS] Desktop Integration Complete!")
    print("=" * 60)
    print()
    print("[INSTALLED] Files:")
    print("   • Desktop entry: ~/.local/share/applications/storymaster.desktop")
    print("   • Icons: ~/.local/share/icons/hicolor/*/apps/storymaster.*")
    print("   • Executable link: ~/.local/bin/storymaster (if found)")
    print()
    print("[NEXT STEPS]")
    print("   1. Restart your file manager (or log out/in)")
    print("   2. The executable should now show your custom icon")
    print("   3. You can launch from application menu")
    print("   4. You can run 'storymaster' from terminal")
    print()
    print("[VERIFY] To test:")
    print("   • Check file manager shows custom icon")
    print("   • Look for Storymaster in application menu")
    print("   • Try: storymaster --help")
    print("=" * 60)


def main():
    """Main installation process"""
    print_header()
    
    # Check if we're in the right directory
    if not Path("assets/storymaster.desktop").exists():
        print("[ERROR] Must run from project root directory")
        print("   cd /path/to/storymaster && python scripts/install_desktop_integration.py")
        sys.exit(1)
    
    # Installation steps
    steps = [
        ("Installing desktop entry", install_desktop_entry),
        ("Installing icons", install_icons),
        ("Creating executable link", create_executable_link),
        ("Updating desktop database", update_desktop_database),
        ("Updating icon cache", update_icon_cache),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n[ERROR] Installation failed at: {step_name}")
            sys.exit(1)
    
    print_completion_info()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during installation: {e}")
        sys.exit(1)