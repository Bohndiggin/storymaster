# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Define data files to include
import glob

datas = []

# Include test data CSVs for seeding
test_data_path = project_dir / 'tests' / 'model' / 'database' / 'test_data'
if test_data_path.exists():
    datas.append((str(test_data_path), 'tests/model/database/test_data'))

# Include .env file if it exists
env_file = project_dir / '.env'
if env_file.exists():
    datas.append((str(env_file), '.'))

# Include UI files using glob
for ui_dir in ['common', 'litographer', 'lorekeeper']:
    ui_pattern = str(project_dir / 'storymaster' / 'view' / ui_dir / '*.ui')
    ui_files = glob.glob(ui_pattern)
    for ui_file in ui_files:
        datas.append((ui_file, f'storymaster/view/{ui_dir}'))

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