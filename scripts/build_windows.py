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
        import PySide6
        print(f"✓ PySide6 available")
        
        # Check Qt6 bin directory
        pyside6_path = Path(PySide6.__file__).parent
        qt_bin_path = pyside6_path / 'Qt6' / 'bin'
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
        print("[ERROR] PySide6 not found")
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
    """Create a minimal spec file for Windows with essential Qt6 components only"""
    minimal_spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# Minimal Windows spec file with essential Qt6 components only

import glob
from pathlib import Path

# Essential data files for UI functionality
datas = []

# Include UI files (essential for PySide6 forms)
print("Including UI files...")
for ui_dir in ['common', 'litographer', 'lorekeeper', 'character_arcs']:
    ui_pattern = f'storymaster/view/{ui_dir}/*.ui'
    ui_files = glob.glob(ui_pattern)
    for ui_file in ui_files:
        datas.append((ui_file, f'storymaster/view/{ui_dir}'))
        print(f"  Added UI file: {ui_file}")

# Include minimal Qt6 plugins for essential functionality only
print("Including minimal Qt6 plugins...")
try:
    import PySide6
    pyside6_path = Path(PySide6.__file__).parent
    plugins_path = pyside6_path / 'Qt6' / 'plugins'
    
    if plugins_path.exists():
        # Include only essential platform plugins
        platforms_path = plugins_path / 'platforms'
        if platforms_path.exists():
            essential_platforms = ['qwindows.dll']  # Only Windows platform
            for platform_dll in essential_platforms:
                platform_path = platforms_path / platform_dll
                if platform_path.exists():
                    datas.append((str(platform_path), 'PySide6/Qt6/plugins/platforms'))
                    print(f"  Added essential platform plugin: {platform_dll}")
        
        # Include only essential image format plugins
        imageformats_path = plugins_path / 'imageformats'
        if imageformats_path.exists():
            essential_formats = ['qico.dll', 'qjpeg.dll', 'qpng.dll']  # Basic image support
            for fmt_dll in essential_formats:
                fmt_path = imageformats_path / fmt_dll
                if fmt_path.exists():
                    datas.append((str(fmt_path), 'PySide6/Qt6/plugins/imageformats'))
                    print(f"  Added essential image format: {fmt_dll}")
        
        # Include only essential iconengines
        iconengines_path = plugins_path / 'iconengines'
        if iconengines_path.exists():
            for icon_dll in iconengines_path.glob('qsvgicon.dll'):
                if icon_dll.is_file():
                    datas.append((str(icon_dll), 'PySide6/Qt6/plugins/iconengines'))
                    print(f"  Added essential icon engine: {icon_dll.name}")
    else:
        print("  Warning: Qt6 plugins directory not found")
        
except ImportError:
    print("  Warning: PySide6 not found during spec creation")

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
    import PySide6
    pyside6_path = Path(PySide6.__file__).parent
    qt_bin_path = pyside6_path / 'Qt6' / 'bin'
    
    if qt_bin_path.exists():
        # Include only essential Qt6 DLLs for minimal build
        print("  Including minimal Qt6 DLLs for Windows compatibility...")
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
        else:
            print("  Warning: No ICU DLLs found")
            
    else:
        print(f"  Error: Qt6 bin directory not found: {qt_bin_path}")
        
except ImportError:
    print("  Error: PySide6 not available during DLL collection")

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
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
        'PySide6.sip',
        'PySide6.QtPrintSupport',
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
        # Get PySide6 Qt bin path for --paths argument
        import PySide6
        pyside6_path = Path(PySide6.__file__).parent
        qt_bin_path = pyside6_path / 'Qt6' / 'bin'
        
        # Use direct PyInstaller with auto-collection instead of spec file
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--log-level=INFO",
            "--collect-all", "PySide6",
            "--hidden-import", "PySide6.QtCore",
            "--hidden-import", "PySide6.QtGui",
            "--hidden-import", "PySide6.QtWidgets",
            "--hidden-import", "PySide6.QtSvg",
            "--hidden-import", "sqlalchemy.dialects.sqlite",
            "--onefile",
            "--console",
            "--name", "storymaster",
            "storymaster/main.py"
        ]

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
            
            # Build failed - no fallback, fail completely
            print(f"[ERROR] Windows build failed (exit code: {process.returncode})")
            print("        No fallback - main spec must succeed")
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

        # Copy world building packages if they exist
        world_building_src = Path("world_building_packages")
        if world_building_src.exists():
            world_building_dest = portable_dir / "world_building_packages"
            shutil.copytree(world_building_src, world_building_dest)
            print("  ✓ Copied world building packages")
        else:
            print("  ⚠ No world building packages found")

        # Copy user guide if exists
        guide_pdf = Path("GUIDE.pdf")
        if guide_pdf.exists():
            shutil.copy2(guide_pdf, portable_dir / "GUIDE.pdf")
            print("  ✓ Copied user guide (GUIDE.pdf)")
        else:
            print("  ⚠ User guide not found (GUIDE.pdf)")

        # Create Windows README
        readme_content = """# Storymaster Portable for Windows

## Quick Start
Double-click `storymaster.exe` to run

## Features
- Standalone executable (no installation required)
- Includes Python runtime and all dependencies
- Portable - works from any folder
- Compatible with Windows 10/11
- Includes world building packages for easy project setup

## Contents
- `storymaster.exe` - Main application
- `GUIDE.pdf` - Complete user guide with tutorials and tips
- `world_building_packages/` - Pre-made world building templates (if included)
- `storymaster.db` - Database file (created on first run)

## File Size
~50MB (includes PySide6 runtime)

## Troubleshooting
- If Windows Defender blocks it, allow the application
- Run as Administrator if database creation fails
- Check Windows Event Viewer for detailed error logs
- Ensure Visual C++ Redistributable 2015-2022 is installed

## First Run
- May take 5-10 seconds to start (loading dependencies)
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
    """Check that the built executable exists"""
    print("[VALIDATE] Checking built executable...")
    
    exe_path = Path("dist/storymaster.exe")
    
    if exe_path.exists():
        exe_size = exe_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Executable created: {exe_path} ({exe_size:.1f} MB)")
        return True
    else:
        print("[ERROR] No executable found")
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
        print("   The complex spec failed, but minimal build succeeded")
        print("   ✓ Includes UI files and essential Qt6 plugins only")
        print("   ✓ Should have better Windows compatibility")
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
