# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(__file__).parent.absolute()

# Define data files to include
datas = [
    # Include test data CSVs for seeding
    (str(project_dir / 'tests' / 'model' / 'database' / 'test_data'), 'tests/model/database/test_data'),
    # Include .env file
    (str(project_dir / '.env'), '.'),
    # Include UI files
    (str(project_dir / 'storymaster' / 'view' / 'common' / '*.ui'), 'storymaster/view/common'),
    (str(project_dir / 'storymaster' / 'view' / 'litographer' / '*.ui'), 'storymaster/view/litographer'),
    (str(project_dir / 'storymaster' / 'view' / 'lorekeeper' / '*.ui'), 'storymaster/view/lorekeeper'),
]

# Hidden imports needed for PyQt6 and SQLAlchemy
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.sql.default_comparator',
    'pkg_resources.extern',
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='storymaster',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='storymaster',
)