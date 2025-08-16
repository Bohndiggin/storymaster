# -*- mode: python ; coding: utf-8 -*-
# Fast build spec for development - minimal bundling

import os
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Minimal data files for faster builds
datas = []

# Include only essential UI files
for ui_dir in ['common']:
    ui_pattern = str(project_dir / 'storymaster' / 'view' / ui_dir / '*.ui')
    import glob
    ui_files = glob.glob(ui_pattern)
    for ui_file in ui_files:
        datas.append((ui_file, f'storymaster/view/{ui_dir}'))

# Include world building packages
world_building_path = project_dir / 'world_building_packages'
if world_building_path.exists():
    datas.append((str(world_building_path), 'world_building_packages'))

# Minimal hidden imports - only core PySide6
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.sip',
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
        # Exclude everything we can for speed
        'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython', 'jupyter', 'notebook', 'tkinter',
        'PySide6.QtNetwork', 'PySide6.QtOpenGL', 'PySide6.QtMultimedia', 'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtQuick', 'PySide6.QtQml',
        'PySide6.QtTest', 'PySide6.QtBluetooth', 'PySide6.QtPositioning', 'PySide6.QtSerialPort',
        'pytest', 'unittest', '_pytest',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='storymaster_dev',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for faster debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)