#!/usr/bin/env python3
"""
Verbose build script that shows all PyInstaller output
Use this when you need to debug build issues
"""

import subprocess
import sys
import time
from pathlib import Path

def main():
    """Verbose build with full output"""
    print("=" * 60)
    print("Storymaster Verbose Build")
    print("=" * 60)
    print("This will show ALL PyInstaller output for debugging.")
    print("Use build_executable.py for normal builds.")
    print()
    
    # Check if spec file exists
    spec_file = Path("storymaster.spec")
    if not spec_file.exists():
        print("ERROR: storymaster.spec not found!")
        return False
    
    try:
        # Clean previous builds
        print("[CLEAN] Cleaning previous builds...")
        import shutil
        if Path("build").exists():
            shutil.rmtree("build")
            print("   Removed build/")
        if Path("dist").exists():
            shutil.rmtree("dist")
            print("   Removed dist/")
        
        print("\n[BUILD] Starting verbose build...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run PyInstaller with maximum verbosity
        cmd = [
            sys.executable, "-m", "PyInstaller", 
            "--clean",
            "--log-level=DEBUG",  # Maximum verbosity
            "--debug=all",        # Debug all imports
            "storymaster.spec"
        ]
        
        print(f"Command: {' '.join(cmd)}")
        print("=" * 60)
        
        # Run with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Show all output in real-time
        line_count = 0
        for line in process.stdout:
            line = line.rstrip()
            if line:
                line_count += 1
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                print(f"[{mins:02d}:{secs:02d}] {line}")
        
        process.wait()
        
        elapsed_time = time.time() - start_time
        mins, secs = divmod(int(elapsed_time), 60)
        
        print("=" * 60)
        print(f"Build completed in {mins:02d}:{secs:02d}")
        print(f"Total output lines: {line_count}")
        
        if process.returncode == 0:
            print("✓ BUILD SUCCESSFUL!")
            
            # Show what was created
            exe_path = Path("dist/storymaster.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"Executable: {exe_path} ({size_mb:.1f} MB)")
            
            return True
        else:
            print(f"✗ BUILD FAILED (return code: {process.returncode})")
            return False
            
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        return False
    except Exception as e:
        print(f"\nBuild error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)