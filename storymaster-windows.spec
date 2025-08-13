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
        print("Including ALL Qt6 plugins for comprehensive Windows build...")
        
        # Include ALL platform plugins
        platforms_path = plugins_path / 'platforms'
        if platforms_path.exists():
            platform_count = 0
            for platform_dll in platforms_path.glob('*.dll'):
                if platform_dll.is_file():
                    datas.append((str(platform_dll), 'PyQt6/Qt6/plugins/platforms'))
                    platform_count += 1
                    print(f"  Added platform plugin: {platform_dll.name}")
            print(f"  Total platform plugins: {platform_count}")
        
        # Include ALL image format plugins
        imageformats_path = plugins_path / 'imageformats'  
        if imageformats_path.exists():
            imageformat_count = 0
            for fmt_dll in imageformats_path.glob('*.dll'):
                if fmt_dll.is_file():
                    datas.append((str(fmt_dll), 'PyQt6/Qt6/plugins/imageformats'))
                    imageformat_count += 1
                    print(f"  Added image format plugin: {fmt_dll.name}")
            print(f"  Total image format plugins: {imageformat_count}")
        
        # Include ALL other Qt6 plugin categories
        plugin_categories = [
            'iconengines', 'styles', 'accessible', 'printsupport',
            'generic', 'bearer', 'audio', 'mediaservice', 'playlistformats',
            'position', 'sensors', 'canbus', 'sqldrivers', 'texttospeech'
        ]
        
        for category in plugin_categories:
            category_path = plugins_path / category
            if category_path.exists():
                category_count = 0
                for plugin_dll in category_path.glob('*.dll'):
                    if plugin_dll.is_file():
                        datas.append((str(plugin_dll), f'PyQt6/Qt6/plugins/{category}'))
                        category_count += 1
                        print(f"  Added {category} plugin: {plugin_dll.name}")
                if category_count > 0:
                    print(f"  Total {category} plugins: {category_count}")

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

# Comprehensive Qt6 hidden imports for full functionality
hiddenimports = [
    # Core Qt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'PyQt6.sip',
    'PyQt6.QtPrintSupport',
    'sip',
    
    # Additional Qt6 modules for comprehensive functionality
    'PyQt6.QtOpenGL',
    'PyQt6.QtOpenGLWidgets',
    'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets',
    'PyQt6.QtNetwork',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngine',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtQuick',
    'PyQt6.QtQml',
    'PyQt6.QtCharts',
    'PyQt6.QtDataVisualization',
    'PyQt6.Qt3DCore',
    'PyQt6.Qt3DRender',
    'PyQt6.Qt3DInput',
    'PyQt6.Qt3DLogic',
    'PyQt6.Qt3DAnimation',
    'PyQt6.Qt3DExtras',
    'PyQt6.QtPositioning',
    'PyQt6.QtLocation',
    'PyQt6.QtSensors',
    'PyQt6.QtSerialPort',
    'PyQt6.QtBluetooth',
    'PyQt6.QtNfc',
    'PyQt6.QtTextToSpeech',
    'PyQt6.QtHelp',
    'PyQt6.QtSql',
    'PyQt6.QtTest',
    'PyQt6.QtConcurrent',
    'PyQt6.QtDBus',
    'PyQt6.QtDesigner',
    'PyQt6.QtUiTools',
    'PyQt6.QtXml',
    'PyQt6.QtSvgWidgets',
    'PyQt6.QtPdf',
    'PyQt6.QtPdfWidgets',
    'PyQt6.QtSpatialAudio',
    'PyQt6.QtHttpServer',
    'PyQt6.QtQuick3D',
    'PyQt6.QtQuickWidgets',
    'PyQt6.QtRemoteObjects',
    'PyQt6.QtScxml',
    'PyQt6.QtStateMachine',
    'PyQt6.QtVirtualKeyboard',
    'PyQt6.QtWebChannel',
    'PyQt6.QtWebSockets',
    
    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.orm',
    'sqlalchemy.engine',
    
    # Essential encodings
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.cp1252',
    'encodings.latin_1',
    'encodings.utf_16',
    'encodings.utf_32',
]

# Simplified binary collection
binaries = []

# Include essential Qt6 DLLs only
try:
    qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
    if qt_bin_path.exists():
        # Include ALL Qt6 DLLs (comprehensive bundle)
        print("Including all Qt6 DLLs for comprehensive Windows build...")
        qt_dll_count = 0
        for qt_dll in qt_bin_path.glob('Qt6*.dll'):
            if qt_dll.is_file():
                binaries.append((str(qt_dll), '.'))
                qt_dll_count += 1
                print(f"  Added Qt6 DLL: {qt_dll.name}")
        
        print(f"  Total Qt6 DLLs included: {qt_dll_count}")
        
        # Also include any other essential Qt dependencies
        other_qt_dlls = ['libEGL.dll', 'libGLESv2.dll', 'opengl32sw.dll']
        for dll_name in other_qt_dlls:
            dll_path = qt_bin_path / dll_name
            if dll_path.exists():
                binaries.append((str(dll_path), '.'))
                print(f"  Added Qt dependency: {dll_name}")
        
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
        # Only exclude non-essential packages that aren't needed
        'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython', 'jupyter',
        'tkinter', 'unittest', 'pytest', '_pytest'
        # Note: Removed PyQt6 exclusions to include all Qt6 libraries
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