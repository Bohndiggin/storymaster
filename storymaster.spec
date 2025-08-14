# -*- mode: python ; coding: utf-8 -*-

import os
import glob
from pathlib import Path

# PyInstaller imports (added automatically by PyInstaller, but explicit for clarity)
try:
    from PyInstaller.building.build_main import Analysis
    from PyInstaller.building.api import PYZ, EXE, COLLECT, BUNDLE
except ImportError:
    # These will be available when PyInstaller processes the spec
    pass

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Define data files to include

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

# Skip enchant data files for now to avoid build issues
print("Skipping enchant data files - spell checking will work without bundled dictionaries")

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
        print(f"  Found: {icon_path}")
        datas.append((str(icon_path), 'assets'))
    else:
        print(f"  Missing: {icon_path}")

# Check version info file
version_file = project_dir / 'version_info.py'
print(f"Version file: {version_file} - {'exists' if version_file.exists() else 'MISSING'}")

# Create version_info.py if it doesn't exist
if not version_file.exists():
    print("Creating version_info.py...")
    try:
        # Create version info directly in the spec file to avoid path issues
        version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=(1,0,0,0),
prodvers=(1,0,0,0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x3f,
# Contains a bitmask that specifies the Boolean attributes of the file.
flags=0x0,
# The operating system for which this file was designed.
# 0x4 - NT and there is no need to change it.
OS=0x40004,
# The general type of file.
# 0x1 - the file is an application.
fileType=0x1,
# The function of the file.
# 0x0 - the function is not defined for this fileType
subtype=0x0,
# Creation date and time stamp.
date=(0, 0)
),
kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'Storymaster Development'),
    StringStruct(u'FileDescription', u'Storymaster - Creative Writing Tool'),
    StringStruct(u'FileVersion', u'1.0.0.0'),
    StringStruct(u'InternalName', u'storymaster'),
    StringStruct(u'LegalCopyright', u'Copyright (C) 2025'),
    StringStruct(u'OriginalFilename', u'storymaster.exe'),
    StringStruct(u'ProductName', u'Storymaster'),
    StringStruct(u'ProductVersion', u'1.0.0.0')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        with open(str(version_file), 'w', encoding='utf-8') as f:
            f.write(version_content)
        print("  Version info created")
    except Exception as e:
        print(f"  Failed to create version info: {e}")

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
    
    # Spell checking dependencies (disabled for now)
    # 'enchant',
    # 'enchant.checker',
]

# Include all essential PyQt6 binaries for cross-platform compatibility
binaries = []

# Include enchant libraries for spell checking
import platform
system_name = platform.system().lower()

# Skip enchant bundling for now to avoid build issues
# PyEnchant will still work if available, but won't be bundled
print("Skipping enchant bundling - spell checking will use system enchant if available")

# Include Python shared library for AppImage compatibility
import sysconfig
python_lib = sysconfig.get_config_var('LDLIBRARY')
if python_lib:
    python_lib_path = Path(sysconfig.get_config_var('LIBDIR')) / python_lib
    if python_lib_path.exists():
        binaries.append((str(python_lib_path), '.'))
        print(f"  Including Python library: {python_lib_path}")
    else:
        print(f"  Python library not found: {python_lib_path}")

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

# Platform-specific executable creation
import platform

if platform.system() == 'Darwin':
    # macOS: Create executable with separate resources for app bundle
    exe = EXE(
        pyz,
        a.scripts,
        exclude_binaries=True,  # Keep binaries separate for COLLECT
        name='storymaster',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(project_dir / 'assets/storymaster_icon_64.png') if (project_dir / 'assets/storymaster_icon_64.png').exists() else None,
    )

    # Create COLLECT for proper macOS app bundle structure
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name='storymaster'
    )

    # Create macOS app bundle
    # Use existing .icns file (preferred) or fall back to PNG
    icns_icon = project_dir / 'assets/storymaster_icon_1024.icns'
    png_icon = project_dir / 'assets/storymaster_icon_1024.png'
    
    if icns_icon.exists():
        icon_path = str(icns_icon)
    elif png_icon.exists():
        icon_path = str(png_icon)
    else:
        icon_path = None
    
    app = BUNDLE(
        coll,
        name='Storymaster.app',
        icon=icon_path,
        bundle_identifier='com.storymaster.app',
        info_plist={
            'CFBundleDisplayName': 'Storymaster',
            'CFBundleName': 'Storymaster',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'LSMinimumSystemVersion': '11.0',  # PyQt6 minimum requirement
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSApplicationCategoryType': 'public.app-category.productivity',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeExtensions': ['db'],
                    'CFBundleTypeName': 'Storymaster Database',
                    'CFBundleTypeRole': 'Editor'
                }
            ],
            'NSPrincipalClass': 'NSApplication'
        }
    )
else:
    # Linux/Windows: Create one-file executable
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
        upx=False,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(project_dir / 'assets/storymaster_icon_64.png') if (project_dir / 'assets/storymaster_icon_64.png').exists() else None,
        # No version info to avoid Windows build hanging
    )