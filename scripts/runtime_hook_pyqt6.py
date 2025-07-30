"""
Runtime hook for PyQt6 to ensure plugins are found properly
"""
import os
import sys
from pathlib import Path

# Set Qt plugin path for bundled executable
if getattr(sys, 'frozen', False):
    # Running in bundled mode
    bundle_dir = Path(sys._MEIPASS)
    qt_plugin_path = bundle_dir / 'PyQt6' / 'Qt6' / 'plugins'
    
    if qt_plugin_path.exists():
        os.environ['QT_PLUGIN_PATH'] = str(qt_plugin_path)
        print(f"Qt plugin path set to: {qt_plugin_path}")
    
    # Also try alternative path structure
    alt_plugin_path = bundle_dir / 'plugins'
    if alt_plugin_path.exists():
        current_path = os.environ.get('QT_PLUGIN_PATH', '')
        if current_path:
            os.environ['QT_PLUGIN_PATH'] = f"{current_path}{os.pathsep}{alt_plugin_path}"
        else:
            os.environ['QT_PLUGIN_PATH'] = str(alt_plugin_path)
        print(f"Additional Qt plugin path: {alt_plugin_path}")
    
    # Set Qt platform plugin path specifically
    platform_path = qt_plugin_path / 'platforms' if qt_plugin_path.exists() else None
    if platform_path and platform_path.exists():
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(platform_path)
        print(f"Qt platform plugin path set to: {platform_path}")