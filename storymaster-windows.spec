# -*- mode: python ; coding: utf-8 -*-

import os
import glob
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Windows-specific data files
datas = []

# Simplified PyQt6 plugin inclusion with error handling
try:
    import PyQt6
    pyqt6_path = Path(PyQt6.__file__).parent
    plugins_path = pyqt6_path / 'Qt6' / 'plugins'

    if plugins_path.exists():
        # Essential platform plugins only
        platforms_path = plugins_path / 'platforms'
        if platforms_path.exists():
            # Only include qwindows.dll which is essential for Windows
            qwindows_dll = platforms_path / 'qwindows.dll'
            if qwindows_dll.exists():
                datas.append((str(qwindows_dll), 'PyQt6/Qt6/plugins/platforms'))
        
        # Essential image format plugins
        imageformats_path = plugins_path / 'imageformats'  
        if imageformats_path.exists():
            essential_formats = ['qico.dll', 'qjpeg.dll', 'qpng.dll']
            for fmt_dll in essential_formats:
                fmt_path = imageformats_path / fmt_dll
                if fmt_path.exists():
                    datas.append((str(fmt_path), 'PyQt6/Qt6/plugins/imageformats'))

except ImportError:
    print("Warning: PyQt6 not found during spec file analysis")

# Include UI files
for ui_dir in ['common', 'litographer', 'lorekeeper', 'character_arcs']:
    ui_pattern = str(project_dir / 'storymaster' / 'view' / ui_dir / '*.ui')
    ui_files = glob.glob(ui_pattern)
    for ui_file in ui_files:
        datas.append((ui_file, f'storymaster/view/{ui_dir}'))

# Include icon files (optional)
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

# Include test data and world building packages (optional)
test_data_path = project_dir / 'tests' / 'model' / 'database' / 'test_data'
if test_data_path.exists():
    datas.append((str(test_data_path), 'tests/model/database/test_data'))

world_building_path = project_dir / 'world_building_packages'
if world_building_path.exists():
    datas.append((str(world_building_path), 'world_building_packages'))

# Minimal essential hidden imports
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'PyQt6.sip',
    'PyQt6.QtPrintSupport',
    'sip',
    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.orm',
    'sqlalchemy.engine',
    # Essential encodings
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.cp1252',
]

# Simplified binary collection
binaries = []

# Include essential Qt6 DLLs only
try:
    qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
    if qt_bin_path.exists():
        # Essential Qt6 DLLs only
        essential_qt_dlls = [
            'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll', 
            'Qt6Svg.dll', 'Qt6PrintSupport.dll'
        ]
        
        for dll_name in essential_qt_dlls:
            dll_path = qt_bin_path / dll_name
            if dll_path.exists():
                binaries.append((str(dll_path), '.'))
        
        # ICU DLLs (required for Qt6 text processing)
        for icu_file in qt_bin_path.glob('icu*.dll'):
            if icu_file.is_file():
                binaries.append((str(icu_file), '.'))

except NameError:
    # PyQt6 not available during spec analysis
    pass

a = Analysis(
    ['storymaster/main.py'],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],  # Remove custom hooks that might cause issues
    hooksconfig={},
    runtime_hooks=[],  # Remove runtime hooks that might cause build failures
    excludes=[
        # Conservative exclusions to avoid dependency issues
        'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython', 'jupyter',
        'tkinter', 'unittest', 'pytest', '_pytest',
        'PyQt6.QtNetwork', 'PyQt6.QtOpenGL', 'PyQt6.QtMultimedia',
        'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtQuick', 'PyQt6.QtQml', 'PyQt6.QtTest'
    ],
    noarchive=False,
    optimize=1,  # Reduce optimization level to avoid issues
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
    console=True,  # Enable console for debugging Windows issues
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Disable icon to avoid build issues
    icon=None,
)