#!/usr/bin/env python3
"""
Simple macOS .icns Creator for Storymaster

Creates .icns file from existing PNG files (no ImageMagick required).
Only requires the iconutil command that comes with macOS.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_header():
    """Print script header"""
    print("=" * 60)
    print("[ICNS] Simple macOS Icon Creator for Storymaster")
    print("   Creates .icns from existing PNGs")
    print("=" * 60)
    print()


def check_iconutil():
    """Check for iconutil (macOS only)"""
    print("[CHECK] Checking for iconutil...")
    
    try:
        result = subprocess.run(['iconutil', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ iconutil found (macOS)")
            return True
        else:
            return False
    except FileNotFoundError:
        print("❌ iconutil not found")
        print("   This script requires macOS with Xcode Command Line Tools")
        print("   Install with: xcode-select --install")
        return False


def check_existing_pngs(assets_dir):
    """Check which PNG files we have"""
    print("[CHECK] Looking for existing PNG files...")
    
    required_sizes = [16, 32, 64, 128, 256, 512, 1024]
    found_pngs = {}
    missing_sizes = []
    
    for size in required_sizes:
        png_file = assets_dir / f"storymaster_icon_{size}.png"
        if png_file.exists():
            found_pngs[size] = png_file
            print(f"  ✅ {size}x{size}")
        else:
            missing_sizes.append(size)
            print(f"  ❌ {size}x{size}")
    
    if missing_sizes:
        print(f"\n⚠️  Missing sizes: {missing_sizes}")
        print("   The .icns will be created with available sizes only")
    
    if not found_pngs:
        print("\n❌ No PNG files found!")
        print("   Expected files like: assets/storymaster_icon_256.png")
        return None
    
    return found_pngs


def create_iconset(assets_dir, found_pngs):
    """Create macOS iconset structure from existing PNGs"""
    print(f"\n[ICONSET] Creating iconset structure...")
    
    iconset_dir = assets_dir / "storymaster_icon.iconset"
    
    # Clean up existing iconset
    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)
    
    iconset_dir.mkdir()
    
    # Icon mapping: (source_size, iconset_name)
    # We'll use what we have available
    icon_mappings = []
    
    # Build mappings based on what PNG files we actually have
    if 16 in found_pngs:
        icon_mappings.append((16, "icon_16x16.png"))
    if 32 in found_pngs:
        icon_mappings.append((32, "icon_32x32.png"))
        if 16 not in found_pngs:  # Use 32 as 16@2x if we don't have 16
            icon_mappings.append((32, "icon_16x16@2x.png"))
    if 64 in found_pngs:
        icon_mappings.append((64, "icon_32x32@2x.png"))
    if 128 in found_pngs:
        icon_mappings.append((128, "icon_128x128.png"))
    if 256 in found_pngs:
        icon_mappings.append((256, "icon_128x128@2x.png"))
        icon_mappings.append((256, "icon_256x256.png"))
    if 512 in found_pngs:
        icon_mappings.append((512, "icon_256x256@2x.png"))
        icon_mappings.append((512, "icon_512x512.png"))
    if 1024 in found_pngs:
        icon_mappings.append((1024, "icon_512x512@2x.png"))
    
    if not icon_mappings:
        print("  ❌ No usable PNG files for iconset")
        return None
    
    # Copy files to iconset
    for source_size, iconset_name in icon_mappings:
        source_file = found_pngs[source_size]
        target_file = iconset_dir / iconset_name
        
        shutil.copy2(source_file, target_file)
        print(f"  ✅ {iconset_name} (from {source_size}x{source_size})")
    
    return iconset_dir


def create_icns(iconset_dir, output_path):
    """Convert iconset to .icns file"""
    print(f"\n[ICNS] Creating {output_path}...")
    
    try:
        cmd = ['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(output_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ {output_path} created successfully!")
            # Clean up iconset directory
            shutil.rmtree(iconset_dir)
            print(f"  🗑️  Cleaned up {iconset_dir}")
            return True
        else:
            print(f"  ❌ iconutil failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ iconutil error: {e}")
        return False


def print_completion_info(icns_path):
    """Print completion information"""
    print("\n" + "=" * 60)
    print("[SUCCESS] macOS .icns Icon Created!")
    print("=" * 60)
    print()
    print(f"📁 Created: {icns_path}")
    print("🔧 Spec file already configured to use it")
    print()
    print("Next steps:")
    print("  1. Run: python scripts/build_macos.py --non-interactive")
    print("  2. Your Storymaster.app will have the castle emoji icon! 🏰")
    print()
    print("Build will now use:")
    print(f"  • {icns_path} (preferred)")
    print("  • assets/storymaster_icon_1024.png (fallback)")
    print("=" * 60)


def main():
    """Main icon creation process"""
    print_header()
    
    # Check project structure
    project_dir = Path(".")
    assets_dir = project_dir / "assets"
    
    if not assets_dir.exists():
        print(f"❌ Assets directory not found: {assets_dir}")
        return False
    
    # Check for iconutil
    if not check_iconutil():
        return False
    
    # Check existing PNG files
    found_pngs = check_existing_pngs(assets_dir)
    if not found_pngs:
        return False
    
    # Create iconset
    iconset_dir = create_iconset(assets_dir, found_pngs)
    if not iconset_dir:
        return False
    
    # Create .icns file
    icns_path = assets_dir / "storymaster_icon.icns"
    if not create_icns(iconset_dir, icns_path):
        return False
    
    print_completion_info(icns_path)
    return True


if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Icon creation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)