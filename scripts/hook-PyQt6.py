"""
PyInstaller hook for PyQt6 to ensure all necessary modules and DLLs are included
"""
from PyInstaller.utils.hooks import collect_all, collect_data_files
from pathlib import Path
import PyQt6

# Collect all PyQt6 modules and data
datas, binaries, hiddenimports = collect_all('PyQt6')

# Add specific PyQt6 DLLs and plugins for Windows
pyqt6_path = Path(PyQt6.__file__).parent

# Include Qt6 bin directory DLLs
qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
if qt_bin_path.exists():
    for dll_file in qt_bin_path.glob('*.dll'):
        if dll_file.is_file():
            binaries.append((str(dll_file), '.'))

# Include Qt6 plugins
qt_plugins_path = pyqt6_path / 'Qt6' / 'plugins'
if qt_plugins_path.exists():
    # Platform plugins (essential for GUI)
    platforms_path = qt_plugins_path / 'platforms'
    if platforms_path.exists():
        for platform_file in platforms_path.iterdir():
            if platform_file.is_file():
                datas.append((str(platform_file), 'PyQt6/Qt6/plugins/platforms'))
    
    # Image format plugins
    imageformats_path = qt_plugins_path / 'imageformats'
    if imageformats_path.exists():
        for img_file in imageformats_path.iterdir():
            if img_file.is_file():
                datas.append((str(img_file), 'PyQt6/Qt6/plugins/imageformats'))

# Add essential hidden imports
hiddenimports.extend([
    'PyQt6.sip',
    'sip',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
])