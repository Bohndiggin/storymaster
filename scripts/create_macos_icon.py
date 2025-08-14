#!/usr/bin/env python3
"""
macOS Icon Generator for Storymaster

Creates proper .icns icon file from SVG source for macOS app bundles.
Generates all required PNG sizes and converts to .icns format.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_header():
    """Print script header"""
    print("=" * 60)
    print("[ICON] macOS Icon Generator for Storymaster")
    print("   Creates .icns from SVG source")
    print("=" * 60)
    print()


def check_dependencies():
    """Check for required tools"""
    print("[CHECK] Checking dependencies...")
    
    # Check for ImageMagick
    try:
        result = subprocess.run(['magick', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ImageMagick found")
            magick_available = True
        else:
            magick_available = False
    except FileNotFoundError:
        magick_available = False
    
    if not magick_available:
        print("❌ ImageMagick not found")
        print("   Install with: brew install imagemagick")
        return False
    
    # Check for iconutil (macOS only)
    try:
        result = subprocess.run(['iconutil', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ iconutil found (macOS)")
            iconutil_available = True
        else:
            iconutil_available = False
    except FileNotFoundError:
        iconutil_available = False
    
    if not iconutil_available:
        print("⚠️  iconutil not found (Linux/Windows)")
        print("   .icns creation will be skipped")
    
    return magick_available, iconutil_available


def create_png_sizes(svg_path, output_dir):
    """Create all required PNG sizes from SVG"""
    print(f"\n[PNG] Creating PNG sizes from {svg_path}...")
    
    # Required sizes for macOS icons
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        output_file = output_dir / f"storymaster_icon_{size}.png"
        
        # Skip if file already exists and is newer than SVG
        if output_file.exists():
            svg_mtime = os.path.getmtime(svg_path)
            png_mtime = os.path.getmtime(output_file)
            if png_mtime > svg_mtime:
                print(f"  ✅ {size}x{size} (already exists)")
                continue
        
        try:
            cmd = [
                'magick',
                str(svg_path),
                '-resize', f'{size}x{size}',
                '-background', 'transparent',
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {size}x{size} created")
            else:
                print(f"  ❌ {size}x{size} failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ {size}x{size} error: {e}")
            return False
    
    return True


def create_iconset(assets_dir):
    """Create macOS iconset structure"""
    print(f"\n[ICONSET] Creating iconset structure...")
    
    iconset_dir = assets_dir / "storymaster_icon.iconset"
    
    # Clean up existing iconset
    if iconset_dir.exists():
        shutil.rmtree(iconset_dir)
    
    iconset_dir.mkdir()
    
    # Icon mapping: (source_size, iconset_name)
    icon_mappings = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),  # 16@2x = 32
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),  # 32@2x = 64
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),  # 128@2x = 256
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),  # 256@2x = 512
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),  # 512@2x = 1024
    ]
    
    for source_size, iconset_name in icon_mappings:
        source_file = assets_dir / f"storymaster_icon_{source_size}.png"
        target_file = iconset_dir / iconset_name
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"  ✅ {iconset_name}")
        else:
            print(f"  ❌ {iconset_name} (source missing: {source_size}x{source_size})")
            return False
    
    return iconset_dir


def create_icns(iconset_dir, output_path):
    """Convert iconset to .icns file"""
    print(f"\n[ICNS] Creating {output_path}...")
    
    try:
        cmd = ['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(output_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ {output_path} created")
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


def update_spec_file(icns_path):
    """Update the PyInstaller spec file to use the new icon"""
    print(f"\n[SPEC] Updating PyInstaller spec file...")
    
    spec_file = Path("storymaster.spec")
    if not spec_file.exists():
        print("  ⚠️  storymaster.spec not found")
        return False
    
    try:
        # Read spec file
        with open(spec_file, 'r') as f:
            content = f.read()
        
        # Check if spec file already has the correct icon setup
        icns_check = f"icon=str(icns_icon) if icns_icon.exists() else None"
        if icns_check in content:
            print(f"  ✅ Spec file already configured for .icns icons")
            return True
        
        # Update the icon path for macOS BUNDLE (fallback for old format)
        old_icon_line = "        icon=None,  # Skip icon for now - would need .icns format"
        new_icon_line = f"        icon=str(project_dir / '{icns_path.relative_to(Path('.'))}'),"
        
        if old_icon_line in content:
            content = content.replace(old_icon_line, new_icon_line)
            
            # Write updated spec file
            with open(spec_file, 'w') as f:
                f.write(content)
            
            print(f"  ✅ Updated spec file to use {icns_path}")
            return True
        else:
            print("  ⚠️  Icon line not found in spec file")
            print(f"  💡 Spec file already configured - {icns_path} will be used automatically")
            return True
    
    except Exception as e:
        print(f"  ❌ Error updating spec file: {e}")
        return False


def print_completion_info(icns_path):
    """Print completion information"""
    print("\n" + "=" * 60)
    print("[SUCCESS] macOS Icon Creation Complete!")
    print("=" * 60)
    print()
    print(f"📁 Created: {icns_path}")
    print("🔧 Updated: storymaster.spec")
    print()
    print("Next steps:")
    print("  1. Run: python scripts/build_macos.py --non-interactive")
    print("  2. Your Storymaster.app will now have a proper icon!")
    print()
    print("Files created:")
    assets_dir = Path("assets")
    for size in [128, 256, 512, 1024]:
        png_file = assets_dir / f"storymaster_icon_{size}.png"
        if png_file.exists():
            print(f"  • {png_file}")
    print(f"  • {icns_path}")
    print("=" * 60)


def main():
    """Main icon creation process"""
    print_header()
    
    # Check project structure
    project_dir = Path(".")
    assets_dir = project_dir / "assets"
    svg_path = assets_dir / "storymaster_icon.svg"
    
    if not svg_path.exists():
        print(f"❌ SVG icon not found: {svg_path}")
        print("   Please ensure you have assets/storymaster_icon.svg")
        return False
    
    # Check dependencies
    deps = check_dependencies()
    if not deps:
        return False
    
    magick_available, iconutil_available = deps
    
    # Create PNG sizes
    if not create_png_sizes(svg_path, assets_dir):
        print("❌ Failed to create PNG sizes")
        return False
    
    # Create .icns file (macOS only)
    if iconutil_available:
        iconset_dir = create_iconset(assets_dir)
        if not iconset_dir:
            print("❌ Failed to create iconset")
            return False
        
        icns_path = assets_dir / "storymaster_icon.icns"
        if not create_icns(iconset_dir, icns_path):
            print("❌ Failed to create .icns file")
            return False
        
        # Update spec file
        update_spec_file(icns_path)
        
        print_completion_info(icns_path)
    else:
        print("\n⚠️  iconutil not available - .icns creation skipped")
        print("   PNG files created, but you'll need to run this on macOS")
        print("   to create the .icns file and update the spec")
    
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