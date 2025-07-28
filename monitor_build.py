#!/usr/bin/env python3
"""
Build progress monitor - shows what files PyInstaller is working on
Run this in a separate terminal while build_executable.py is running
"""

import time
from pathlib import Path
import os

def monitor_build_progress():
    """Monitor build directory for progress"""
    print("🔍 Build Progress Monitor")
    print("=" * 40)
    print("Monitoring build/ and dist/ directories...")
    print("Press Ctrl+C to stop")
    print()
    
    last_build_count = 0
    last_dist_count = 0
    start_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            elapsed = int(current_time - start_time)
            mins, secs = divmod(elapsed, 60)
            
            # Check build directory
            build_dir = Path("build")
            build_count = 0
            if build_dir.exists():
                build_count = sum(1 for _ in build_dir.rglob("*") if _.is_file())
            
            # Check dist directory
            dist_dir = Path("dist")
            dist_count = 0
            if dist_dir.exists():
                dist_count = sum(1 for _ in dist_dir.rglob("*") if _.is_file())
            
            # Show progress
            status_line = f"[{mins:02d}:{secs:02d}] Build: {build_count} files | Dist: {dist_count} files"
            
            # Show changes
            if build_count != last_build_count or dist_count != last_dist_count:
                print(status_line)
                
                # Show what's happening
                if build_count > last_build_count:
                    print("   → Analyzing/collecting files...")
                elif dist_count > last_dist_count:
                    print("   → Creating executable...")
                
                last_build_count = build_count
                last_dist_count = dist_count
            
            # Check if build is complete
            exe_path = Path("dist/storymaster.exe")
            if exe_path.exists() and exe_path.stat().st_size > 1024 * 1024:  # > 1MB
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\n🎉 Build appears complete!")
                print(f"   Executable: {exe_path} ({size_mb:.1f} MB)")
                break
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

def show_build_tips():
    """Show tips for monitoring builds"""
    print("\n💡 Build Monitoring Tips:")
    print("=" * 40)
    print("1. Normal Windows build takes 5-10 minutes")
    print("2. Build files appear in build/ first, then dist/")
    print("3. Final executable is usually 80-150 MB")
    print("4. If build/ stops growing, check for errors")
    print("5. Use build_verbose.py to see detailed output")
    print()
    print("🔧 Build Scripts Available:")
    print("   python build_executable.py  - Normal build")
    print("   python build_fast.py        - Quick dev build") 
    print("   python build_verbose.py     - Debug build")
    print()

def main():
    """Main monitor function"""
    show_build_tips()
    
    # Check if a build is already in progress
    if Path("build").exists() or Path("dist").exists():
        response = input("Build directories exist. Monitor anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    monitor_build_progress()

if __name__ == "__main__":
    main()