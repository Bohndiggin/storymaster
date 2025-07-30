# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Define data files to include
import glob

datas = []

# Include all essential PyQt6 plugins for cross-platform AppImage compatibility
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
    
    # Include ALL image format plugins
    imageformats_path = plugins_path / 'imageformats'  
    if imageformats_path.exists():
        for img_file in imageformats_path.glob('*'):
            if img_file.is_file():
                datas.append((str(img_file), 'PyQt6/Qt6/plugins/imageformats'))
    
    # Include other essential plugin directories for full compatibility
    essential_plugin_dirs = ['xcbglintegrations', 'wayland-decoration-client', 
                           'wayland-graphics-integration-client', 'wayland-shell-integration',
                           'generic', 'iconengines']
    for plugin_dir in essential_plugin_dirs:
        plugin_path = plugins_path / plugin_dir
        if plugin_path.exists():
            for plugin_file in plugin_path.glob('*'):
                if plugin_file.is_file():
                    datas.append((str(plugin_file), f'PyQt6/Qt6/plugins/{plugin_dir}'))

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
    
    # Comprehensive SQLAlchemy 2.0+ modules for AppImage compatibility
    'sqlalchemy',
    'sqlalchemy.ext',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.ext.hybrid',
    'sqlalchemy.orm',
    'sqlalchemy.orm.events',
    'sqlalchemy.orm.state',
    'sqlalchemy.orm.strategies',
    'sqlalchemy.orm.loading',
    'sqlalchemy.orm.persistence',
    'sqlalchemy.orm.collections',
    'sqlalchemy.orm.relationships',
    'sqlalchemy.orm.scoping',
    'sqlalchemy.orm.session',
    'sqlalchemy.orm.sync',
    'sqlalchemy.orm.unitofwork',
    'sqlalchemy.orm.util',
    'sqlalchemy.dialects',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.dialects.sqlite.base',
    'sqlalchemy.dialects.sqlite.pysqlite',
    'sqlalchemy.sql',
    'sqlalchemy.sql.base',
    'sqlalchemy.sql.compiler',
    'sqlalchemy.sql.crud',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.sql.dml',
    'sqlalchemy.sql.elements',
    'sqlalchemy.sql.expression',
    'sqlalchemy.sql.functions',
    'sqlalchemy.sql.operators',
    'sqlalchemy.sql.schema',
    'sqlalchemy.sql.selectable',
    'sqlalchemy.sql.sqltypes',
    'sqlalchemy.sql.type_api',
    'sqlalchemy.sql.visitors',
    'sqlalchemy.engine',
    'sqlalchemy.engine.base',
    'sqlalchemy.engine.create',
    'sqlalchemy.engine.cursor',
    'sqlalchemy.engine.default',
    'sqlalchemy.engine.events',
    'sqlalchemy.engine.interfaces',
    'sqlalchemy.engine.reflection',
    'sqlalchemy.engine.result',
    'sqlalchemy.engine.row',
    'sqlalchemy.engine.strategies',
    'sqlalchemy.engine.url',
    'sqlalchemy.engine.util',
    'sqlalchemy.pool',
    'sqlalchemy.pool.base',
    'sqlalchemy.pool.impl',
    'sqlalchemy.pool.events',
    'sqlalchemy.types',
    'sqlalchemy.util',
    'sqlalchemy.util._collections',
    'sqlalchemy.util.compat',
    'sqlalchemy.util.deprecations',
    'sqlalchemy.util.langhelpers',
    'sqlalchemy.util.queue',
    'sqlalchemy.util.topological',
    'sqlalchemy.events',
    'sqlalchemy.inspection',
    'sqlalchemy.log',
    'sqlalchemy.schema',
    
    # Other minimal dependencies
    'pkg_resources.extern',
    
    # Spell checking dependencies (only if needed)
    'enchant',
    'enchant.checker',
]

# Include all essential PyQt6 binaries for cross-platform compatibility
binaries = []
if plugins_path.exists():
    # Include Qt libraries for all platforms (Linux .so, Windows .dll)
    qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
    qt_lib_path = pyqt6_path / 'Qt6' / 'lib'
    
    # Check both bin and lib directories
    for lib_dir in [qt_bin_path, qt_lib_path]:
        if lib_dir.exists():
            # Include all Qt6 core libraries for complete compatibility
            for lib_file in lib_dir.glob('libQt6*'):
                if lib_file.is_file():
                    binaries.append((str(lib_file), '.'))
            for lib_file in lib_dir.glob('Qt6*.dll'):
                if lib_file.is_file():
                    binaries.append((str(lib_file), '.'))
            for lib_file in lib_dir.glob('Qt6*.so*'):
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
    icon=str(project_dir / 'assets/storymaster_icon.ico') if os.name == 'nt' and (project_dir / 'assets/storymaster_icon.ico').exists() else (str(project_dir / 'assets/storymaster_icon_64.png') if (project_dir / 'assets/storymaster_icon_64.png').exists() else None),
    version=str(project_dir / 'version_info.py') if (project_dir / 'version_info.py').exists() else None,
)

# Note: For one-file mode, no COLLECT is needed
# The executable includes everything in a single file