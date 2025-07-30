# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Define data files to include
import glob

datas = []

# Include only essential PyQt6 platform plugins (for faster builds)
import PyQt6
pyqt6_path = Path(PyQt6.__file__).parent
plugins_path = pyqt6_path / 'Qt6' / 'plugins'
if plugins_path.exists():
    # Include only essential platform plugins
    platforms_path = plugins_path / 'platforms'
    if platforms_path.exists():
        # Only include Windows platform plugin to speed up build
        essential_platforms = ['qwindows.dll', 'qwindows.so', 'qoffscreen.dll', 'qoffscreen.so']
        for platform_name in essential_platforms:
            platform_file = platforms_path / platform_name
            if platform_file.exists():
                datas.append((str(platform_file), 'PyQt6/Qt6/plugins/platforms'))
    
    # Include only essential image format plugins
    imageformats_path = plugins_path / 'imageformats'
    if imageformats_path.exists():
        # Only include common image formats to reduce size
        essential_formats = ['qico.dll', 'qjpeg.dll', 'qpng.dll', 'qsvg.dll', 
                            'qico.so', 'qjpeg.so', 'qpng.so', 'qsvg.so']
        for format_name in essential_formats:
            img_file = imageformats_path / format_name
            if img_file.exists():
                datas.append((str(img_file), 'PyQt6/Qt6/plugins/imageformats'))

# Include test data CSVs for seeding
test_data_path = project_dir / 'tests' / 'model' / 'database' / 'test_data'
if test_data_path.exists():
    datas.append((str(test_data_path), 'tests/model/database/test_data'))

# Include world building packages
world_building_path = project_dir / 'world_building_packages'
if world_building_path.exists():
    datas.append((str(world_building_path), 'world_building_packages'))

# Note: .env file not needed - using hardcoded defaults in code

# Include UI files using glob
for ui_dir in ['common', 'litographer', 'lorekeeper', 'character_arcs']:
    ui_pattern = str(project_dir / 'storymaster' / 'view' / ui_dir / '*.ui')
    ui_files = glob.glob(ui_pattern)
    for ui_file in ui_files:
        datas.append((ui_file, f'storymaster/view/{ui_dir}'))

# Include icon assets
icon_files = [
    'assets/storymaster_icon.ico',
    'assets/storymaster_icon.svg', 
    'assets/storymaster_icon_16.png',
    'assets/storymaster_icon_32.png',
    'assets/storymaster_icon_64.png'
]
print("Checking icon files:")
for icon_file in icon_files:
    icon_path = project_dir / icon_file
    if icon_path.exists():
        print(f"  ✓ Found: {icon_path}")
        datas.append((str(icon_path), 'assets'))
    else:
        print(f"  ✗ Missing: {icon_path}")

# Check version info file
version_file = project_dir / 'version_info.py'
print(f"Version file: {version_file} - {'exists' if version_file.exists() else 'MISSING'}")

# Hidden imports needed for PyQt6 and SQLAlchemy
hiddenimports = [
    # Core PyQt6 modules (only what we actually use)
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'PyQt6.sip',
    
    # Only essential additional PyQt6 modules 
    'PyQt6.QtPrintSupport',
    
    # SQLAlchemy modules (only essential ones)
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.engine.default',
    'sqlalchemy.pool',
    
    # Other minimal dependencies
    'pkg_resources.extern',
    
    # Spell checking dependencies (only if needed)
    'enchant',
    'enchant.checker',
]

# Include only essential PyQt6 binaries for Windows
binaries = []
if plugins_path.exists():
    # Include only essential Qt libraries to reduce build time
    qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
    if qt_bin_path.exists():
        # Only include core Qt DLLs, not all of them
        essential_qt_libs = [
            'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll', 
            'Qt6Svg.dll', 'Qt6PrintSupport.dll'
        ]
        for lib_name in essential_qt_libs:
            lib_path = qt_bin_path / lib_name
            if lib_path.exists():
                binaries.append((str(lib_path), '.'))

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
        # Exclude unnecessary modules to reduce size and build time
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'tkinter',
        # Additional Qt modules we don't need
        'PyQt6.QtNetwork',
        'PyQt6.QtOpenGL',
        'PyQt6.QtMultimedia',
        'PyQt6.QtWebEngine',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtQuick',
        'PyQt6.QtQml',
        'PyQt6.QtTest',
        'PyQt6.QtBluetooth',
        'PyQt6.QtPositioning',
        'PyQt6.QtSerialPort',
        # Test modules
        'pytest',
        'unittest',
        '_pytest',
    ],
    noarchive=False,
    optimize=2,  # Enable Python bytecode optimization
)

pyz = PYZ(a.pure)

# Create one-file executable for easier distribution
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
    upx=False,  # Disable UPX compression - reduces false positives
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_dir / 'assets/storymaster_icon.ico') if (project_dir / 'assets/storymaster_icon.ico').exists() else None,
    version=str(project_dir / 'version_info.py') if (project_dir / 'version_info.py').exists() else None,
)

# Note: For one-file mode, no COLLECT is needed
# The executable includes everything in a single file