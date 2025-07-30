#!/usr/bin/env python3
"""
GitHub Actions optimized build script
Faster, more reliable builds for CI environment
"""

import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

def print_header():
    """Print build header"""
    print("=" * 50)
    print("GitHub Actions Optimized Build")
    print("Fast directory-mode executable")
    print("=" * 50)

def clean_previous_builds():
    """Clean up previous build artifacts"""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    print("Clean complete")
    return True

def build_executable():
    """Build executable using optimized spec"""
    print("Building executable (directory mode)...")
    print("This should take 2-5 minutes...")
    
    start_time = time.time()
    
    try:
        # Use GitHub Actions optimized spec
        cmd = [
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "--log-level=WARN",  # Less verbose for CI
            "storymaster_github.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        # Run with timeout protection
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            timeout=900  # 15 minute timeout
        )
        
        elapsed = time.time() - start_time
        print(f"Build completed in {elapsed:.1f} seconds")
        
        if process.returncode == 0:
            print("✓ Build successful!")
            
            # Check if executable exists
            system = platform.system().lower()
            if system == "windows":
                exe_path = Path("dist/storymaster/storymaster.exe")
            else:
                exe_path = Path("dist/storymaster/storymaster")
            
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"✓ Executable created: {exe_path} ({size_mb:.1f} MB)")
                return True
            else:
                print("✗ Executable not found at expected location")
                return False
        else:
            print("✗ Build failed!")
            print("STDERR:", process.stderr[-1000:])  # Last 1000 chars
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Build timed out after 15 minutes")
        return False
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def create_archive():
    """Create distribution archive"""
    print("Creating distribution archive...")
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Create archive name
    archive_name = f"storymaster-{system}-{arch}"
    
    try:
        if system == "windows":
            # Create ZIP for Windows
            shutil.make_archive(archive_name, "zip", "dist", "storymaster")
            print(f"✓ Created: {archive_name}.zip")
        else:
            # Create tar.gz for Unix systems
            shutil.make_archive(archive_name, "gztar", "dist", "storymaster")
            print(f"✓ Created: {archive_name}.tar.gz")
        
        return True
    except Exception as e:
        print(f"✗ Archive creation failed: {e}")
        return False

def print_completion():
    """Print completion info"""
    print("\n" + "=" * 50)
    print("GitHub Actions Build Complete!")
    print("=" * 50)
    
    system = platform.system()
    
    print("Files created:")
    print(f"  • Directory: dist/storymaster/")
    print(f"  • Archive: storymaster-{system.lower()}-*.{'zip' if system == 'Windows' else 'tar.gz'}")
    print()
    print("Optimizations used:")
    print("  • Directory mode (not one-file)")
    print("  • Minimal dependencies")
    print("  • No version info (faster)")
    print("  • Essential plugins only")
    print("  • 15-minute timeout protection")

def main():
    """Main build process"""
    print_header()
    
    steps = [
        ("Cleaning builds", clean_previous_builds),
        ("Building executable", build_executable),
        ("Creating archive", create_archive),
    ]
    
    for step_name, step_func in steps:
        print(f"\n[{step_name.upper()}]")
        if not step_func():
            print(f"✗ Failed at: {step_name}")
            sys.exit(1)
    
    print_completion()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✗ Build cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)