# -*- mode: python ; coding: utf-8 -*-

import os
import glob
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Windows-specific data files
datas = []

# Include PyQt6 plugins for Windows
import PyQt6
pyqt6_path = Path(PyQt6.__file__).parent
plugins_path = pyqt6_path / 'Qt6' / 'plugins'

if plugins_path.exists():
    # Windows platform plugins
    platforms_path = plugins_path / 'platforms'
    if platforms_path.exists():
        for platform_file in platforms_path.glob('*'):
            if platform_file.is_file():
                datas.append((str(platform_file), 'PyQt6/Qt6/plugins/platforms'))
    
    # Image format plugins
    imageformats_path = plugins_path / 'imageformats'  
    if imageformats_path.exists():
        for img_file in imageformats_path.glob('*'):
            if img_file.is_file():
                datas.append((str(img_file), 'PyQt6/Qt6/plugins/imageformats'))

# Include UI files
for ui_dir in ['common', 'litographer', 'lorekeeper', 'character_arcs']:
    ui_pattern = str(project_dir / 'storymaster' / 'view' / ui_dir / '*.ui')
    ui_files = glob.glob(ui_pattern)
    for ui_file in ui_files:
        datas.append((ui_file, f'storymaster/view/{ui_dir}'))

# Include Windows icon files
icon_files = [
    'assets/storymaster_icon.ico',
    'assets/storymaster_icon_16.png',
    'assets/storymaster_icon_32.png',
    'assets/storymaster_icon_64.png'
]

for icon_file in icon_files:
    icon_path = project_dir / icon_file
    if icon_path.exists():
        datas.append((str(icon_path), 'assets'))

# Include test data and world building packages
test_data_path = project_dir / 'tests' / 'model' / 'database' / 'test_data'
if test_data_path.exists():
    datas.append((str(test_data_path), 'tests/model/database/test_data'))

world_building_path = project_dir / 'world_building_packages'
if world_building_path.exists():
    datas.append((str(world_building_path), 'world_building_packages'))

# Windows-specific hidden imports (minimal for faster builds)
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'PyQt6.sip',
    'PyQt6.QtPrintSupport',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.orm',
    'sqlalchemy.engine',
]

# Windows-specific binaries
binaries = []

# Include Qt6 DLLs for Windows
qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
if qt_bin_path.exists():
    for lib_file in qt_bin_path.glob('Qt6*.dll'):
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
        # Aggressive exclusions for Windows to reduce size and build time
        'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython', 'jupyter',
        'tkinter', 'unittest', 'pytest', '_pytest',
        'PyQt6.QtNetwork', 'PyQt6.QtOpenGL', 'PyQt6.QtMultimedia',
        'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtQuick', 'PyQt6.QtQml', 'PyQt6.QtTest'
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

# Windows-specific EXE with conservative settings
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='storymaster',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX on Windows to avoid issues
    runtime_tmpdir=None,
    console=False,  # Windows GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Use icon only if it exists and isn't causing issues
    icon=str(project_dir / 'assets/storymaster_icon.ico') if (project_dir / 'assets/storymaster_icon.ico').exists() else None,
)