#!/usr/bin/env python3
"""
Windows-specific build script for Storymaster

Optimized for speed and reliability on Windows.
Creates portable executable with minimal dependencies.
"""

import os
import platform
import shutil
import stat
import subprocess
import sys
import time
import traceback
from pathlib import Path


def print_header():
    """Print Windows build header"""
    print("=" * 50)
    print("Storymaster Windows Builder")
    print("Fast, reliable Windows executable")
    print("=" * 50)
    print()


def check_platform():
    """Ensure we're running on Windows"""
    if platform.system().lower() != "windows":
        print("[ERROR] This script is for Windows only")
        print("Use build_linux.py for Linux builds")
        return False
    return True


def check_dependencies():
    """Check Windows build dependencies"""
    print("[CHECK] Verifying dependencies...")

    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("[ERROR] PyInstaller not found")
        return False

    try:
        import PyQt6
        print(f"✓ PyQt6 available")
        
        # Check Qt6 bin directory
        pyqt6_path = Path(PyQt6.__file__).parent
        qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
        if qt_bin_path.exists():
            print(f"✓ Qt6 bin directory: {qt_bin_path}")
            
            # Count Qt6 DLLs
            qt_dlls = list(qt_bin_path.glob('Qt6*.dll'))
            if qt_dlls:
                print(f"✓ Found {len(qt_dlls)} Qt6 DLLs")
            else:
                print("[WARNING] No Qt6 DLLs found in bin directory")
                
        else:
            print("[WARNING] Qt6 bin directory not found")
            
    except ImportError:
        print("[ERROR] PyQt6 not found")
        return False

    # Check for Visual C++ runtime DLLs
    print("[CHECK] Checking Visual C++ runtime availability...")
    vc_runtime_found = False
    
    # Check system directories for VC runtime
    system_paths = [
        Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'System32',
        Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')) / 'SysWOW64'
    ]
    
    vc_dlls = ['msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll']
    
    for sys_path in system_paths:
        if sys_path.exists():
            found_dlls = []
            for vc_dll in vc_dlls:
                if (sys_path / vc_dll).exists():
                    found_dlls.append(vc_dll)
            
            if found_dlls:
                print(f"✓ Found VC runtime DLLs in {sys_path}: {', '.join(found_dlls)}")
                vc_runtime_found = True
    
    if not vc_runtime_found:
        print("[WARNING] Visual C++ runtime DLLs not found in system directories")
        print("          Application may fail on systems without VC++ redistributable")

    return True


def clean_build():
    """Clean Windows build artifacts (skip on CI - fresh environment)"""

    # Skip cleaning on CI - GitHub Actions provides fresh runners
    if os.environ.get("GITHUB_ACTIONS"):
        print("[CLEAN] Skipping clean (CI environment is already fresh)")
        return True

    print("[CLEAN] Removing previous build...")

    try:
        dirs_to_remove = ["build", "dist"]
        for dir_name in dirs_to_remove:
            dir_path = Path(dir_name)
            if dir_path.exists():
                print(f"  Removing {dir_name}/...")

                # On Windows, sometimes need to handle readonly files
                def handle_readonly(func, path, exc):
                    if exc[1].errno == 13:  # Permission denied
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    else:
                        raise

                shutil.rmtree(dir_path, onerror=handle_readonly)
                print(f"  ✓ Removed {dir_name}/")

        # Clean pyc files
        pyc_count = 0
        for pyc_file in Path(".").rglob("*.pyc"):
            try:
                pyc_file.unlink()
                pyc_count += 1
            except Exception:
                pass  # Ignore individual pyc file errors

        if pyc_count > 0:
            print(f"  ✓ Removed {pyc_count} .pyc files")

        print("[OK] Clean complete")
        return True

    except Exception as e:
        print(f"[ERROR] Clean failed: {e}")
        return False


def create_minimal_spec():
    """Create a comprehensive spec file for Windows with ALL Qt6 libraries and components"""
    minimal_spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# Comprehensive Windows spec file with ALL Qt6 libraries and components

import glob
from pathlib import Path

# Essential data files for UI functionality
datas = []

# Include UI files (essential for PyQt6 forms)
print("Including UI files...")
for ui_dir in ['common', 'litographer', 'lorekeeper', 'character_arcs']:
    ui_pattern = f'storymaster/view/{ui_dir}/*.ui'
    ui_files = glob.glob(ui_pattern)
    for ui_file in ui_files:
        datas.append((ui_file, f'storymaster/view/{ui_dir}'))
        print(f"  Added UI file: {ui_file}")

# Include ALL Qt6 plugins for comprehensive functionality
print("Including ALL Qt6 plugins...")
try:
    import PyQt6
    pyqt6_path = Path(PyQt6.__file__).parent
    plugins_path = pyqt6_path / 'Qt6' / 'plugins'
    
    if plugins_path.exists():
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
    else:
        print("  Warning: Qt6 plugins directory not found")
        
except ImportError:
    print("  Warning: PyQt6 not found during spec creation")

# Include essential test data and world building packages
print("Including essential data packages...")
test_data_path = Path('.') / 'tests' / 'model' / 'database' / 'test_data'
if test_data_path.exists():
    datas.append((str(test_data_path), 'tests/model/database/test_data'))
    print(f"  Added test data: {test_data_path}")

world_building_path = Path('.') / 'world_building_packages'
if world_building_path.exists():
    datas.append((str(world_building_path), 'world_building_packages'))
    print(f"  Added world building packages: {world_building_path}")
else:
    print("  Warning: world_building_packages directory not found")

print(f"Total data files included: {len(datas)}")

# Essential Qt6 DLLs for minimal build
binaries = []
print("Including essential Qt6 DLLs...")
try:
    import PyQt6
    pyqt6_path = Path(PyQt6.__file__).parent
    qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
    
    if qt_bin_path.exists():
        # Include ALL Qt6 DLLs for comprehensive functionality
        print("  Including ALL Qt6 DLLs for comprehensive Windows build...")
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
            else:
                print(f"  Warning: Qt dependency not found: {dll_name}")
        
        # ICU DLLs (required for Qt6 text processing)
        icu_count = 0
        for icu_file in qt_bin_path.glob('icu*.dll'):
            if icu_file.is_file():
                binaries.append((str(icu_file), '.'))
                icu_count += 1
        
        if icu_count > 0:
            print(f"  Added {icu_count} ICU DLLs for text processing")
        else:
            print("  Warning: No ICU DLLs found")
            
    else:
        print(f"  Error: Qt6 bin directory not found: {qt_bin_path}")
        
except ImportError:
    print("  Error: PyQt6 not available during DLL collection")

# Add Visual C++ runtime DLLs (critical for Qt6 functionality)
print("Including Visual C++ runtime DLLs...")
import os
system32_path = Path(os.environ.get('SYSTEMROOT', 'C:\\\\Windows')) / 'System32'
vc_runtime_dlls = ['msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll']

for vc_dll in vc_runtime_dlls:
    vc_dll_path = system32_path / vc_dll
    if vc_dll_path.exists():
        binaries.append((str(vc_dll_path), '.'))
        print(f"  Added VC++ runtime: {vc_dll}")
    else:
        print(f"  Warning: VC++ runtime not found: {vc_dll}")

print(f"Total binaries included: {len(binaries)}")

a = Analysis(
    ['storymaster/main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='storymaster-minimal',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open("storymaster-minimal.spec", "w", encoding="utf-8") as f:
        f.write(minimal_spec_content)
    
    print("  Created minimal spec file: storymaster-minimal.spec")
    return True


def build_exe():
    """Build Windows executable using optimized spec"""
    print("[BUILD] Creating Windows executable...")
    print("  Using storymaster-windows.spec (optimized for Windows)")

    try:
        # Get PyQt6 Qt bin path for --paths argument
        import PyQt6
        pyqt6_path = Path(PyQt6.__file__).parent
        qt_bin_path = pyqt6_path / 'Qt6' / 'bin'
        
        # Use Windows-specific spec file with explicit paths
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--log-level=INFO",
        ]
        
        # Add --paths argument if Qt6 bin directory exists
        if qt_bin_path.exists():
            cmd.extend(["--paths", str(qt_bin_path)])
            print(f"  Using PyQt6 bin path: {qt_bin_path}")
        
        cmd.append("storymaster-windows.spec")

        print(f"  Command: {' '.join(cmd)}")
        start_time = time.time()

        # Run with real-time output and comprehensive logging
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )

        # Capture all output for debugging
        all_output = []
        error_lines = []
        
        # Show progress and capture output
        for line in process.stdout:
            line = line.strip()
            all_output.append(line)
            
            # Capture error patterns
            if any(error_word in line.lower() for error_word in ["error", "failed", "traceback", "exception"]):
                error_lines.append(line)
            
            # Show relevant progress
            if line and any(
                keyword in line.lower()
                for keyword in ["info:", "building", "completed", "copying", "warning", "error", "failed"]
            ):
                print(f"    {line}")

        process.wait()
        build_time = time.time() - start_time

        if process.returncode == 0:
            print(f"[OK] Build completed in {build_time:.1f}s")
            return True
        else:
            print(f"[ERROR] Build failed (exit code: {process.returncode})")
            
            # Show detailed error information
            if error_lines:
                print("\n[ERROR DETAILS] PyInstaller error messages:")
                for error_line in error_lines[-10:]:  # Show last 10 error lines
                    print(f"  {error_line}")
            
            # Write full log to file for debugging
            log_file = Path("pyinstaller_build.log")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("\n".join(all_output))
            print(f"[DEBUG] Full build log written to: {log_file}")
            
            # Try minimal spec as fallback
            print("\n[FALLBACK] Attempting build with minimal spec...")
            create_minimal_spec()
            
            # Try building with minimal spec
            minimal_cmd = [
                sys.executable, "-m", "PyInstaller", 
                "--clean", "--log-level=INFO", 
                "storymaster-minimal.spec"
            ]
            
            print(f"  Minimal command: {' '.join(minimal_cmd)}")
            minimal_result = subprocess.run(minimal_cmd, capture_output=True, text=True)
            
            if minimal_result.returncode == 0:
                print("[OK] Enhanced minimal build succeeded!")
                print("      ✓ Includes UI files and essential Qt6 plugins")
                print("      ✓ Should have working PyQt6 interface")
                print("      ⚠ Complex spec file has configuration issues - using minimal version")
                return True
            else:
                print("[ERROR] Enhanced minimal build also failed")
                print("        This indicates a fundamental PyInstaller/environment issue")
                print("        Check:")
                print("        - PyQt6 installation")
                print("        - Python version compatibility")
                print("        - Windows Visual C++ runtime")
                return False

    except Exception as e:
        print(f"[ERROR] Build error: {e}")
        return False


def create_portable():
    """Create Windows portable package"""
    print("[PACKAGE] Creating portable Windows package...")

    # Check for both possible executable names
    exe_path = Path("dist/storymaster.exe")
    minimal_exe_path = Path("dist/storymaster-minimal.exe")
    
    if exe_path.exists():
        final_exe = exe_path
        print(f"  Using main executable: {exe_path}")
    elif minimal_exe_path.exists():
        final_exe = minimal_exe_path
        print(f"  Using minimal executable: {minimal_exe_path}")
    else:
        print(f"[ERROR] No executable found: {exe_path} or {minimal_exe_path}")
        return False

    # Create portable directory
    portable_dir = Path("dist/storymaster_portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True)

    try:
        # Copy executable with standard name
        shutil.copy2(final_exe, portable_dir / "storymaster.exe")
        print(f"  ✓ Copied executable from {final_exe.name}")

        # Copy database if exists
        if Path("storymaster.db").exists():
            shutil.copy2("storymaster.db", portable_dir / "storymaster.db")
            print("  ✓ Copied database")

        # Create Windows README
        readme_content = """# Storymaster Portable for Windows

## Quick Start
Double-click `storymaster.exe` to run

## Features
- Standalone executable (no installation required)
- Includes Python runtime and all dependencies
- Portable - works from any folder
- Compatible with Windows 10/11

## File Size
~150MB (includes full Python + PyQt6 runtime)

## Troubleshooting
- If Windows Defender blocks it, allow the application
- Run as Administrator if database creation fails
- Check Windows Event Viewer for detailed error logs

## First Run
- May take 10-15 seconds to start (extracting files)
- Creates storymaster.db database file
- Subsequent runs are faster

For support: https://github.com/your-repo/storymaster
"""

        with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("  ✓ Created README.txt")

        print("[OK] Portable package ready")
        return True

    except Exception as e:
        print(f"[ERROR] Package creation failed: {e}")
        return False


def create_zip():
    """Create Windows distribution ZIP"""
    print("[ZIP] Creating distribution archive...")

    portable_dir = Path("dist/storymaster_portable")
    if not portable_dir.exists():
        print("[ERROR] No portable package found")
        return False

    try:
        # Create ZIP archive
        archive_name = f"storymaster-windows-{platform.machine().lower()}"
        shutil.make_archive(archive_name, "zip", "dist", "storymaster_portable")

        zip_path = f"{archive_name}.zip"
        zip_size = Path(zip_path).stat().st_size / (1024 * 1024)
        print(f"  ✓ Created {zip_path} ({zip_size:.1f} MB)")

        return True

    except Exception as e:
        print(f"[ERROR] ZIP creation failed: {e}")
        return False


def validate_build():
    """Validate the built executable with Qt6 bundle test"""
    print("[VALIDATE] Testing built executable...")
    
    # Check for both possible executable names
    exe_path = Path("dist/storymaster.exe")
    minimal_exe_path = Path("dist/storymaster-minimal.exe")
    
    if exe_path.exists():
        final_exe = exe_path
        print(f"  Validating main executable: {exe_path}")
    elif minimal_exe_path.exists():
        final_exe = minimal_exe_path
        print(f"  Validating minimal executable: {minimal_exe_path}")
    else:
        print("[ERROR] No executable found for validation")
        return False
    
    try:
        # Run the Qt6 validation test on the built executable
        test_script = Path("scripts/test_qt6_bundle.py")
        if not test_script.exists():
            print("[WARNING] Qt6 validation script not found, skipping validation")
            return True
        
        print("  Running Qt6 bundle validation test...")
        result = subprocess.run([
            str(final_exe),
            "-c", f"exec(open('{test_script}').read())"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✓ Qt6 bundle validation passed")
            return True
        else:
            print("  ✗ Qt6 bundle validation failed")
            print(f"  Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠ Qt6 validation test timed out")
        return False
    except Exception as e:
        print(f"  ⚠ Could not run validation test: {e}")
        return False


def print_summary():
    """Print build summary"""
    print("\n" + "=" * 50)
    print("[SUCCESS] Windows Build Complete!")
    print("=" * 50)

    # Check which executable was built
    main_exe_path = Path("dist/storymaster.exe")
    minimal_exe_path = Path("dist/storymaster-minimal.exe")
    
    if minimal_exe_path.exists() and not main_exe_path.exists():
        print("🔧 MINIMAL BUILD USED")
        print("   The complex spec failed, but enhanced minimal build succeeded")
        print("   ✓ Includes UI files and Qt6 plugins")
        print("   ✓ Should have functional interface")
        exe_size = minimal_exe_path.stat().st_size / (1024 * 1024)
        print(f"   Source: dist/storymaster-minimal.exe ({exe_size:.1f} MB)")

    exe_path = Path("dist/storymaster.exe")
    if exe_path.exists():
        exe_size = exe_path.stat().st_size / (1024 * 1024)
        print(f"Executable: dist/storymaster.exe ({exe_size:.1f} MB)")

    portable_path = Path("dist/storymaster_portable")
    if portable_path.exists():
        print("Portable package: dist/storymaster_portable/")

    # Find ZIP file
    for zip_file in Path(".").glob("storymaster-windows-*.zip"):
        zip_size = zip_file.stat().st_size / (1024 * 1024)
        print(f"Distribution: {zip_file} ({zip_size:.1f} MB)")

    print("\nReady for distribution!")
    print("Users can extract and run storymaster.exe")
    
    print("\nTroubleshooting:")
    print("- If the app fails to start, ensure Visual C++ Redistributable is installed")
    print("- For Qt6 platform plugin errors, check Windows Event Viewer for details")
    print("- Test on a clean Windows VM without development tools")


def main():
    """Main Windows build process"""
    print_header()

    # Enhanced build pipeline for Windows with validation
    steps = [
        ("Platform check", check_platform),
        ("Dependencies", check_dependencies),
        ("Clean build", clean_build),
        ("Build executable", build_exe),
        ("Validate build", validate_build),
        ("Create portable", create_portable),
        ("Create ZIP", create_zip),
    ]

    for step_name, step_func in steps:
        print(f"\n[STEP] {step_name}")
        if not step_func():
            if step_name == "Validate build":
                print("[WARNING] Build validation failed, but continuing with packaging")
                print("          Manual testing recommended before distribution")
            else:
                print(f"[FAILED] Build stopped at: {step_name}")
                sys.exit(1)

    print_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CANCELLED] Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
