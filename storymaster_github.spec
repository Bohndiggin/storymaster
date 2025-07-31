# -*- mode: python ; coding: utf-8 -*-
# GitHub Actions optimized build spec - faster, directory mode

import os
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Minimal data files for GitHub Actions build
datas = []

# Include UI files - essential for app to work
import glob
for ui_dir in ['common', 'litographer', 'lorekeeper', 'character_arcs']:
    ui_pattern = str(project_dir / 'storymaster' / 'view' / ui_dir / '*.ui')
    ui_files = glob.glob(ui_pattern)
    for ui_file in ui_files:
        datas.append((ui_file, f'storymaster/view/{ui_dir}'))

# Include essential PyQt6 plugins for cross-platform AppImage compatibility
import PyQt6
pyqt6_path = Path(PyQt6.__file__).parent
plugins_path = pyqt6_path / 'Qt6' / 'plugins'
if plugins_path.exists():
    # Include ALL platform plugins for cross-platform support
    platforms_path = plugins_path / 'platforms'
    if platforms_path.exists():
        for platform_file in platforms_path.glob('*'):
            if platform_file.is_file():
                datas.append((str(platform_file), 'PyQt6/Qt6/plugins/platforms'))
    
    # Include essential Linux plugin directories for AppImage
    essential_plugin_dirs = ['xcbglintegrations', 'generic']
    for plugin_dir in essential_plugin_dirs:
        plugin_path = plugins_path / plugin_dir
        if plugin_path.exists():
            for plugin_file in plugin_path.glob('*'):
                if plugin_file.is_file():
                    datas.append((str(plugin_file), f'PyQt6/Qt6/plugins/{plugin_dir}'))

# Essential icon (just the main one for GitHub Actions)
main_icon = project_dir / 'assets/storymaster_icon.ico'
if main_icon.exists():
    datas.append((str(main_icon), 'assets'))

# Include world building packages
world_building_path = project_dir / 'world_building_packages'
if world_building_path.exists():
    datas.append((str(world_building_path), 'world_building_packages'))

# Essential hidden imports for AppImage compatibility
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',  # Re-enable for icon support
    'PyQt6.sip',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.engine.default',
    'sqlalchemy.orm',
    'sqlalchemy.sql',
    'sqlalchemy.engine',
]

# Include Python shared library for AppImage compatibility
binaries = []
import sysconfig
python_lib = sysconfig.get_config_var('LDLIBRARY')
if python_lib:
    python_lib_path = Path(sysconfig.get_config_var('LIBDIR')) / python_lib
    if python_lib_path.exists():
        binaries.append((str(python_lib_path), '.'))
        print(f"  ✓ Including Python library: {python_lib_path}")
    else:
        print(f"  ✗ Python library not found: {python_lib_path}")

# Include essential PyQt6 libraries for Linux AppImage
if plugins_path.exists():
    qt_lib_path = pyqt6_path / 'Qt6' / 'lib'
    if qt_lib_path.exists():
        # Include essential Qt6 libraries for Linux
        for lib_file in qt_lib_path.glob('libQt6Core.so*'):
            if lib_file.is_file():
                binaries.append((str(lib_file), '.'))
        for lib_file in qt_lib_path.glob('libQt6Gui.so*'):
            if lib_file.is_file():
                binaries.append((str(lib_file), '.'))
        for lib_file in qt_lib_path.glob('libQt6Widgets.so*'):
            if lib_file.is_file():
                binaries.append((str(lib_file), '.'))

a = Analysis(
    ['storymaster/main.py'],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['scripts/runtime_hook_pyqt6.py'],
    excludes=[
        # Exclude everything we don't need for faster build
        'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython',
        'jupyter', 'notebook', 'tkinter', 'enchant',
        'PyQt6.QtNetwork', 'PyQt6.QtOpenGL', 'PyQt6.QtMultimedia',
        'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtQuick', 'PyQt6.QtQml', 'PyQt6.QtTest', 'PyQt6.QtBluetooth',
        'PyQt6.QtPositioning', 'PyQt6.QtSerialPort',
        'PyQt6.QtPrintSupport', 'pytest', 'unittest', '_pytest',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

# Use DIRECTORY mode for faster, more reliable builds in CI
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='storymaster',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(main_icon) if main_icon.exists() else None,
    # Skip version info for CI builds to avoid hanging
)

# Directory mode - more reliable than one-file for CI
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='storymaster'
)