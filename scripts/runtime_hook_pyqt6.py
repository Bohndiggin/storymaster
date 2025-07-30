"""
Runtime hook for PyQt6 to ensure plugins are found properly in AppImage and other environments
"""
import os
import sys
from pathlib import Path

# Set Qt plugin path for bundled executable
if getattr(sys, 'frozen', False):
    # Running in bundled mode (PyInstaller)
    bundle_dir = Path(sys._MEIPASS)
    qt_plugin_path = bundle_dir / 'PyQt6' / 'Qt6' / 'plugins'
    
    # AppImage detection - AppImages set APPIMAGE and APPDIR environment variables
    is_appimage = os.environ.get('APPIMAGE') or os.environ.get('APPDIR')
    
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
    
    # AppImage-specific environment setup
    if is_appimage:
        print("Running in AppImage environment")
        # Clear problematic environment variables that might interfere
        env_vars_to_clear = ['LD_LIBRARY_PATH', 'PYTHONPATH', 'QML_IMPORT_PATH', 'QML2_IMPORT_PATH']
        for var in env_vars_to_clear:
            if var in os.environ:
                print(f"Clearing environment variable: {var}")
                del os.environ[var]
        
        # Set AppImage-specific Qt settings
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
        
        # Ensure we use the bundled libraries, not system ones
        bundle_lib_path = bundle_dir
        if bundle_lib_path.exists():
            current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
            new_ld_path = str(bundle_lib_path)
            if current_ld_path:
                new_ld_path = f"{new_ld_path}{os.pathsep}{current_ld_path}"
            os.environ['LD_LIBRARY_PATH'] = new_ld_path
            print(f"Updated LD_LIBRARY_PATH for AppImage: {new_ld_path}")
    
    # Additional debugging for troubleshooting
    print(f"Python executable: {sys.executable}")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"Bundle directory: {bundle_dir}")
    print(f"AppImage detected: {bool(is_appimage)}")
    if is_appimage:
        print(f"APPIMAGE: {os.environ.get('APPIMAGE', 'Not set')}")
        print(f"APPDIR: {os.environ.get('APPDIR', 'Not set')}")