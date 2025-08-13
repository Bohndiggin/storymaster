"""
Windows-specific runtime hook to ensure Qt6 DLLs are properly loaded
"""

import os
import sys
from pathlib import Path

def setup_qt_environment():
    """Set up Qt6 environment for Windows PyInstaller bundle"""
    if not (getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")):
        return

    bundle_dir = Path(sys._MEIPASS)
    print(f"[Qt6 Setup] Bundle directory: {bundle_dir}")

    # 1. Add bundle directory to DLL search path (Windows 10+ with Python 3.8+)
    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(str(bundle_dir))
            print(f"[Qt6 Setup] Added DLL directory: {bundle_dir}")
        except (OSError, AttributeError) as e:
            print(f"[Qt6 Setup] Failed to add DLL directory: {e}")

    # 2. Fallback: add to PATH for all Windows versions
    current_path = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{bundle_dir}{os.pathsep}{current_path}"
    print(f"[Qt6 Setup] Updated PATH with bundle directory")

    # 3. Set Qt plugin paths - try multiple possible locations
    qt_plugin_candidates = [
        bundle_dir / "PyQt6" / "Qt6" / "plugins",
        bundle_dir / "plugins",
        bundle_dir / "qt6_plugins",
        bundle_dir / "PyQt6" / "plugins"
    ]

    valid_plugin_paths = []
    for plugin_path in qt_plugin_candidates:
        if plugin_path.exists():
            valid_plugin_paths.append(str(plugin_path))
            print(f"[Qt6 Setup] Found Qt plugin path: {plugin_path}")

    if valid_plugin_paths:
        current_qt_path = os.environ.get("QT_PLUGIN_PATH", "")
        all_paths = valid_plugin_paths + ([current_qt_path] if current_qt_path else [])
        os.environ["QT_PLUGIN_PATH"] = os.pathsep.join(all_paths)
        print(f"[Qt6 Setup] Set QT_PLUGIN_PATH: {os.environ['QT_PLUGIN_PATH']}")

    # 4. Set platform plugin path specifically (critical for Windows)
    platform_candidates = [
        bundle_dir / "PyQt6" / "Qt6" / "plugins" / "platforms",
        bundle_dir / "plugins" / "platforms",
        bundle_dir / "platforms"
    ]

    for platform_path in platform_candidates:
        if platform_path.exists():
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platform_path)
            print(f"[Qt6 Setup] Set QT_QPA_PLATFORM_PLUGIN_PATH: {platform_path}")
            
            # Verify qwindows.dll exists
            qwindows_dll = platform_path / "qwindows.dll"
            if qwindows_dll.exists():
                print(f"[Qt6 Setup] ✓ Found qwindows.dll at {qwindows_dll}")
            else:
                print(f"[Qt6 Setup] ⚠ qwindows.dll not found in {platform_path}")
            break

    # 5. Set additional Qt environment variables for robustness
    os.environ["QT_QPA_PLATFORM"] = "windows"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # 6. Debug: List all DLLs in bundle directory
    dll_count = 0
    qt_dll_count = 0
    for dll_file in bundle_dir.glob("*.dll"):
        dll_count += 1
        if dll_file.name.startswith("Qt6"):
            qt_dll_count += 1
    
    print(f"[Qt6 Setup] Found {dll_count} total DLLs, {qt_dll_count} Qt6 DLLs")
    print(f"[Qt6 Setup] Windows bundle setup complete")

# Execute setup immediately when imported
setup_qt_environment()
