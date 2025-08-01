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
    except ImportError:
        print("[ERROR] PyQt6 not found")
        return False

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


def build_exe():
    """Build Windows executable using optimized spec"""
    print("[BUILD] Creating Windows executable...")
    print("  Using storymaster-windows.spec (optimized for Windows)")

    try:
        # Use Windows-specific spec file
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--log-level=INFO",
            "storymaster-windows.spec",
        ]

        print(f"  Command: {' '.join(cmd)}")
        start_time = time.time()

        # Run with real-time output
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )

        # Show progress
        for line in process.stdout:
            line = line.strip()
            if line and any(
                keyword in line.lower()
                for keyword in ["info:", "building", "completed", "copying", "warning"]
            ):
                print(f"    {line}")

        process.wait()
        build_time = time.time() - start_time

        if process.returncode == 0:
            print(f"[OK] Build completed in {build_time:.1f}s")
            return True
        else:
            print(f"[ERROR] Build failed (exit code: {process.returncode})")
            return False

    except Exception as e:
        print(f"[ERROR] Build error: {e}")
        return False


def create_portable():
    """Create Windows portable package"""
    print("[PACKAGE] Creating portable Windows package...")

    exe_path = Path("dist/storymaster.exe")
    if not exe_path.exists():
        print(f"[ERROR] Executable not found: {exe_path}")
        return False

    # Create portable directory
    portable_dir = Path("dist/storymaster_portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True)

    try:
        # Copy executable
        shutil.copy2(exe_path, portable_dir / "storymaster.exe")
        print("  ✓ Copied executable")

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


def print_summary():
    """Print build summary"""
    print("\n" + "=" * 50)
    print("[SUCCESS] Windows Build Complete!")
    print("=" * 50)

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


def main():
    """Main Windows build process"""
    print_header()

    # Fast build pipeline for Windows
    steps = [
        ("Platform check", check_platform),
        ("Dependencies", check_dependencies),
        ("Clean build", clean_build),
        ("Build executable", build_exe),
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
