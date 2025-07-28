# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Define data files to include
import glob

datas = []

# Include PyQt6 platform plugins (essential for Windows)
import PyQt6
pyqt6_path = Path(PyQt6.__file__).parent
plugins_path = pyqt6_path / 'Qt6' / 'plugins'
if plugins_path.exists():
    # Include platform plugins
    platforms_path = plugins_path / 'platforms'
    if platforms_path.exists():
        for platform_file in platforms_path.glob('*.dll'):
            datas.append((str(platform_file), 'PyQt6/Qt6/plugins/platforms'))
        for platform_file in platforms_path.glob('*.so'):
            datas.append((str(platform_file), 'PyQt6/Qt6/plugins/platforms'))
    
    # Include image format plugins
    imageformats_path = plugins_path / 'imageformats'
    if imageformats_path.exists():
        for img_file in imageformats_path.glob('*.dll'):
            datas.append((str(img_file), 'PyQt6/Qt6/plugins/imageformats'))
        for img_file in imageformats_path.glob('*.so'):
            datas.append((str(img_file), 'PyQt6/Qt6/plugins/imageformats'))

# Include test data CSVs for seeding
test_data_path = project_dir / 'tests' / 'model' / 'database' / 'test_data'
if test_data_path.exists():
    datas.append((str(test_data_path), 'tests/model/database/test_data'))

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
for icon_file in icon_files:
    if (project_dir / icon_file).exists():
        datas.append((str(project_dir / icon_file), 'assets'))

# Hidden imports needed for PyQt6 and SQLAlchemy
hiddenimports = [
    # Core PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'PyQt6.sip',
    
    # Additional PyQt6 modules that may be needed
    'PyQt6.QtPrintSupport',
    'PyQt6.QtNetwork',
    'PyQt6.QtOpenGL',
    
    # PyQt6 platform plugins (critical for Windows)
    'PyQt6.QtCore.QCoreApplication',
    'PyQt6.QtWidgets.QApplication',
    
    # SQLAlchemy modules
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.engine.default',
    'sqlalchemy.pool',
    'sqlalchemy.engine.reflection',
    'sqlalchemy.sql.sqltypes',
    
    # Other dependencies
    'pkg_resources.extern',
    'email.mime.text',
    'email.mime.multipart',
    
    # Spell checking dependencies
    'enchant',
    'enchant.checker',
    'enchant.errors',
]

# Include PyQt6 binaries for Windows
binaries = []
if plugins_path.exists():
    # Include Qt libraries that might be needed
    qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
    if qt_bin_path.exists():
        for qt_lib in qt_bin_path.glob('*.dll'):
            binaries.append((str(qt_lib), '.'))

a = Analysis(
    ['storymaster/main.py'],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook_pyqt6.py'],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'tkinter',
    ],
    noarchive=False,
    optimize=0,
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
    icon='assets/storymaster_icon.ico',  # Icon for Windows
    version='version_info.py',  # Add version info to reduce false positives
)

# Note: For one-file mode, no COLLECT is needed
# The executable includes everything in a single file