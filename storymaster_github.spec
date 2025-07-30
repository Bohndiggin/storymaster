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

# Include minimal PyQt6 plugins for Windows
import PyQt6
pyqt6_path = Path(PyQt6.__file__).parent
plugins_path = pyqt6_path / 'Qt6' / 'plugins'
if plugins_path.exists():
    # Only Windows platform plugin for faster build
    platforms_path = plugins_path / 'platforms'
    if platforms_path.exists():
        platform_file = platforms_path / 'qwindows.dll'
        if platform_file.exists():
            datas.append((str(platform_file), 'PyQt6/Qt6/plugins/platforms'))

# Essential icon (just the main one for GitHub Actions)
main_icon = project_dir / 'assets/storymaster_icon.ico'
if main_icon.exists():
    datas.append((str(main_icon), 'assets'))

# Include world building packages
world_building_path = project_dir / 'world_building_packages'
if world_building_path.exists():
    datas.append((str(world_building_path), 'world_building_packages'))

# Minimal hidden imports - only what's absolutely needed
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.engine.default',
]

a = Analysis(
    ['storymaster/main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude everything we don't need for faster build
        'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython',
        'jupyter', 'notebook', 'tkinter', 'enchant',
        'PyQt6.QtNetwork', 'PyQt6.QtOpenGL', 'PyQt6.QtMultimedia',
        'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtQuick', 'PyQt6.QtQml', 'PyQt6.QtTest', 'PyQt6.QtBluetooth',
        'PyQt6.QtPositioning', 'PyQt6.QtSerialPort', 'PyQt6.QtSvg',
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