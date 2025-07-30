#!/usr/bin/env python3
"""
Fast build script for development testing
Uses minimal bundling for faster build times
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Fast build for development"""
    print("=" * 40)
    print("Fast Development Build")
    print("=" * 40)
    print("WARNING: This is a minimal build for testing only!")
    print("For distribution, use build_executable.py instead.")
    print()
    
    try:
        # Clean previous builds
        import shutil
        if Path("build").exists():
            shutil.rmtree("build")
        if Path("dist").exists():
            shutil.rmtree("dist")
        
        print("Building with minimal bundling...")
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--log-level=ERROR", "storymaster_fast.spec"]
        
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("\n✓ Fast build complete!")
            print("Executable: dist/storymaster_dev.exe")
            print("\nNOTE: This build may not work on other systems.")
            print("It's intended for local development testing only.")
        else:
            print("Build failed!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed: {e}")
        return False
    except Exception as e:
        print(f"Build error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)