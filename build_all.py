#!/usr/bin/env python3
"""
Master Build Script for Storymaster

Creates all available distribution formats:
- Cross-platform executables (PyInstaller)
- Linux RPM packages
- Linux AppImage (universal binary)
- Windows installer (future)
- macOS app bundle (future)
"""

import os
import sys
import platform
import subprocess
from pathlib import Path


def print_header():
    """Print build header"""
    print("=" * 70)
    print("[FACTORY] Storymaster Master Builder")
    print("   Complete distribution package creation")
    print("=" * 70)
    print()
    print(f"[DESKTOP]  Platform: {platform.system()} {platform.machine()}")
    print(f"[PYTHON] Python: {sys.version.split()[0]}")
    print()


def run_build_script(script_name, description):
    """Run a build script and return success status"""
    print("=" * 50)
    print(f"[COMPILE] Building: {description}")
    print("=" * 50)
    
    try:
        # Split script name and arguments
        script_parts = script_name.split()
        script_cmd = [sys.executable] + script_parts
        
        result = subprocess.run(script_cmd, check=True)
        print(f"[OK] {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed with code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"[ERROR] Build script not found: {script_name}")
        return False


def main():
    """Main build orchestrator"""
    import sys
    
    print_header()
    
    # Check for non-interactive mode (CI/CD)
    non_interactive = len(sys.argv) > 1 and sys.argv[1] == "--non-interactive"
    
    # Define available build targets
    build_targets = []
    
    # Always available: PyInstaller executable
    build_targets.append(("build_executable.py", "Cross-platform Executable"))
    
    # Linux-specific builds
    if platform.system() == "Linux":
        build_targets.append(("build_appimage.py", "Linux AppImage (Universal Binary)"))
        build_targets.append(("build_rpm.py", "Linux RPM Package"))
    
    # Future: Windows-specific builds
    if platform.system() == "Windows":
        # build_targets.append(("build_windows_installer.py", "Windows Installer"))
        pass
    
    # macOS builds (native or cross-compilation)
    if platform.system() == "Darwin":
        build_targets.append(("build_macos.py --non-interactive", "macOS App Bundle & DMG"))
    else:
        # Cross-compilation option for macOS
        build_targets.append(("build_macos.py --non-interactive", "macOS App Bundle (Cross-compile)"))
    
    if not build_targets:
        print("[ERROR] No build targets available for this platform")
        return False
    
    if non_interactive:
        # In CI/CD, build all targets
        selected_targets = build_targets
        print("Non-interactive mode: Building all available targets")
    else:
        print("[CHECK] Available build targets:")
        for i, (script, description) in enumerate(build_targets, 1):
            print(f"   {i}. {description}")
        print(f"   {len(build_targets) + 1}. Build all")
        print()
        
        # Get user choice
        while True:
            try:
                choice = input("Select build target (number): ").strip()
                
                if choice == str(len(build_targets) + 1):
                    # Build all
                    selected_targets = build_targets
                    break
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(build_targets):
                        selected_targets = [build_targets[choice_num - 1]]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(build_targets) + 1}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n[ERROR] Build cancelled by user")
                return False
    
    print()
    
    # Execute selected builds
    success_count = 0
    total_count = len(selected_targets)
    
    for script, description in selected_targets:
        if run_build_script(script, description):
            success_count += 1
        print()  # Space between builds
    
    # Summary
    print("=" * 70)
    print("[STATS] Build Summary")
    print("=" * 70)
    print(f"[OK] Successful builds: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n[SUCCESS] All builds completed successfully!")
        
        # List created files
        print("\n[FILES] Distribution files created:")
        distribution_files = [
            ("dist/storymaster/", "Executable directory"),
            ("storymaster-*.tar.gz", "Executable archive"),
            ("storymaster-*.zip", "Executable archive (Windows)"),
            ("Storymaster-x86_64.AppImage", "Linux universal binary"),
            ("~/rpmbuild/RPMS/noarch/storymaster-*.rpm", "RPM package"),
        ]
        
        for file_pattern, description in distribution_files:
            if any(Path(".").glob(file_pattern.replace("~/", str(Path.home()) + "/"))):
                print(f"   • {file_pattern} - {description}")
        
        print("\n[CHECK] Next steps:")
        print("   1. Test the distribution packages on target systems")
        print("   2. Upload to release/download locations")
        print("   3. Update documentation with download links")
        print("   4. Announce the release!")
        
    else:
        failed_count = total_count - success_count
        print(f"[ERROR] {failed_count} build(s) failed")
        print("   Check the error messages above for details")
        return False
    
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[WARNING]  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during build: {e}")
        sys.exit(1)