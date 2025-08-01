"""
Windows-specific runtime hook to ensure Qt6 DLLs are properly loaded
"""
import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    bundle_dir = Path(sys._MEIPASS)
    
    # Add bundle directory to DLL search path (Windows only)
    if hasattr(os, 'add_dll_directory'):
        # Windows 10+ with Python 3.8+
        try:
            os.add_dll_directory(str(bundle_dir))
            print(f"Added DLL directory: {bundle_dir}")
        except (OSError, AttributeError):
            pass
    
    # Fallback: add to PATH for older Windows versions
    current_path = os.environ.get('PATH', '')
    os.environ['PATH'] = f"{bundle_dir}{os.pathsep}{current_path}"
    
    # Set Qt plugin paths for Windows
    qt_plugin_paths = [
        bundle_dir / 'PyQt6' / 'Qt6' / 'plugins',
        bundle_dir / 'plugins'
    ]
    
    for plugin_path in qt_plugin_paths:
        if plugin_path.exists():
            current_qt_path = os.environ.get('QT_PLUGIN_PATH', '')
            if current_qt_path:
                os.environ['QT_PLUGIN_PATH'] = f"{current_qt_path}{os.pathsep}{plugin_path}"
            else:
                os.environ['QT_PLUGIN_PATH'] = str(plugin_path)
    
    # Set platform plugin path specifically
    platform_path = bundle_dir / 'PyQt6' / 'Qt6' / 'plugins' / 'platforms'
    if platform_path.exists():
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(platform_path)
    
    print(f"Windows bundle setup complete. Bundle dir: {bundle_dir}")