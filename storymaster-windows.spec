# -*- mode: python ; coding: utf-8 -*-

import os
import glob
from pathlib import Path

# Get the absolute path to the project directory
project_dir = Path(os.getcwd())

# Windows-specific data files
datas = []

# Minimal PyQt6 plugin inclusion for better compatibility
try:
    import PyQt6
    pyqt6_path = Path(PyQt6.__file__).parent
    plugins_path = pyqt6_path / 'Qt6' / 'plugins'

    if plugins_path.exists():
        print("Including minimal Qt6 plugins for Windows compatibility...")
        
        # Include only essential platform plugins
        platforms_path = plugins_path / 'platforms'
        if platforms_path.exists():
            essential_platforms = ['qwindows.dll']  # Only Windows platform
            for platform_dll in essential_platforms:
                platform_path = platforms_path / platform_dll
                if platform_path.exists():
                    datas.append((str(platform_path), 'PyQt6/Qt6/plugins/platforms'))
                    print(f"  Added essential platform plugin: {platform_dll}")
        
        # Include only essential image format plugins
        imageformats_path = plugins_path / 'imageformats'  
        if imageformats_path.exists():
            essential_formats = ['qico.dll', 'qjpeg.dll', 'qpng.dll']  # Basic image support
            for fmt_dll in essential_formats:
                fmt_path = imageformats_path / fmt_dll
                if fmt_path.exists():
                    datas.append((str(fmt_path), 'PyQt6/Qt6/plugins/imageformats'))
                    print(f"  Added essential image format: {fmt_dll}")
        
        # Include only essential iconengines
        iconengines_path = plugins_path / 'iconengines'
        if iconengines_path.exists():
            for icon_dll in iconengines_path.glob('qsvgicon.dll'):
                if icon_dll.is_file():
                    datas.append((str(icon_dll), 'PyQt6/Qt6/plugins/iconengines'))
                    print(f"  Added essential icon engine: {icon_dll.name}")

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

# Minimal Qt6 hidden imports for essential functionality only
hiddenimports = [
    # Core Qt6 modules (essential)
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtSvg',
    'PyQt6.sip',
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

# Include only essential Qt6 DLLs for minimal build
try:
    qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
    if qt_bin_path.exists():
        # Include only essential Qt6 DLLs
        print("Including minimal Qt6 DLLs for Windows compatibility...")
        essential_qt_dlls = [
            'Qt6Core.dll',      # Core Qt functionality 
            'Qt6Gui.dll',       # GUI components
            'Qt6Widgets.dll',   # Widget toolkit
            'Qt6Svg.dll',       # SVG support (for icons)
        ]
        
        for dll_name in essential_qt_dlls:
            dll_path = qt_bin_path / dll_name
            if dll_path.exists():
                binaries.append((str(dll_path), '.'))
                print(f"  Added essential Qt6 DLL: {dll_name}")
            else:
                print(f"  Warning: Essential DLL not found: {dll_name}")
        
        # ICU DLLs (required for Qt6 text processing)
        icu_count = 0
        for icu_file in qt_bin_path.glob('icu*.dll'):
            if icu_file.is_file():
                binaries.append((str(icu_file), '.'))
                icu_count += 1
        
        if icu_count > 0:
            print(f"  Added {icu_count} ICU DLLs for text processing")

except NameError:
    # PyQt6 not available during spec analysis
    pass

# Add Visual C++ runtime DLLs (critical for Qt6 functionality)
print("Including Visual C++ runtime DLLs...")
import os
system32_path = Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'System32'
vc_runtime_dlls = ['msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll']

for vc_dll in vc_runtime_dlls:
    vc_dll_path = system32_path / vc_dll
    if vc_dll_path.exists():
        binaries.append((str(vc_dll_path), '.'))
        print(f"  Added VC++ runtime: {vc_dll}")
    else:
        print(f"  Warning: VC++ runtime not found: {vc_dll}")

a = Analysis(
    ['storymaster/main.py'],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={
        # Let PyInstaller collect all PyQt6 dependencies automatically
        'pyqt6': {'auto-collection': True}
    },
    runtime_hooks=[],
    excludes=[
        # Exclude heavy packages that aren't needed
        'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython', 'jupyter',
        'tkinter', 'unittest', 'pytest', '_pytest',
        # Exclude non-essential Qt6 modules for minimal build
        'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore',
        'PyQt6.QtQuick', 'PyQt6.QtQml', 'PyQt6.QtCharts', 'PyQt6.QtDataVisualization',
        'PyQt6.Qt3DCore', 'PyQt6.Qt3DRender', 'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets',
        'PyQt6.QtOpenGL', 'PyQt6.QtOpenGLWidgets', 'PyQt6.QtNetwork', 'PyQt6.QtPositioning'
    ],
    noarchive=False,
    optimize=0,  # No optimization to avoid dependency issues
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