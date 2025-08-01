"""
Utility functions for handling world building packages
"""

import os
import sys
from pathlib import Path
from typing import Optional


def get_world_building_packages_path() -> Optional[str]:
    """
    Get the path to the world_building_packages directory with proper error handling
    for both development and AppImage/frozen environments.
    
    Returns:
        Optional[str]: Path to world_building_packages directory, or None if not found
    """
    
    # Possible locations to check
    possible_paths = []
    
    # Method 1: Check if we're in a frozen/bundled environment (AppImage, PyInstaller, etc.)
    if getattr(sys, 'frozen', False):
        # Running in bundled mode
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle
            bundle_dir = Path(sys._MEIPASS)
            possible_paths.append(bundle_dir / "world_building_packages")
        
        # Also try relative to the executable
        exe_dir = Path(sys.executable).parent
        possible_paths.append(exe_dir / "world_building_packages")
    
    # Method 2: Standard development path (relative to main.py)
    main_file = Path(__file__).resolve()
    # Go up from: storymaster/view/common/package_utils.py -> project root
    project_root = main_file.parent.parent.parent.parent
    possible_paths.append(project_root / "world_building_packages")
    
    # Method 3: Legacy method (4 directories up from this file)
    legacy_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "world_building_packages"
    )
    possible_paths.append(Path(legacy_path))
    
    # Method 4: Check current working directory
    possible_paths.append(Path.cwd() / "world_building_packages")
    
    # Method 5: Check relative to sys.argv[0] (the script that was executed)
    if sys.argv and sys.argv[0]:
        script_dir = Path(sys.argv[0]).parent.resolve()
        possible_paths.append(script_dir / "world_building_packages")
    
    # Check each possible path
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return str(path)
    
    return None


def get_world_building_packages_path_debug() -> tuple[Optional[str], list[str]]:
    """
    Debug version that returns both the found path and all attempted paths
    for troubleshooting AppImage issues.
    
    Returns:
        tuple[Optional[str], list[str]]: (found_path, attempted_paths)
    """
    
    attempted_paths = []
    
    # Possible locations to check
    possible_paths = []
    
    # Method 1: Check if we're in a frozen/bundled environment
    if getattr(sys, 'frozen', False):
        attempted_paths.append(f"Detected frozen environment: sys.frozen = {sys.frozen}")
        
        if hasattr(sys, '_MEIPASS'):
            bundle_dir = Path(sys._MEIPASS)
            bundle_path = bundle_dir / "world_building_packages"
            possible_paths.append(bundle_path)
            attempted_paths.append(f"PyInstaller bundle path: {bundle_path}")
        
        exe_dir = Path(sys.executable).parent
        exe_path = exe_dir / "world_building_packages"
        possible_paths.append(exe_path)
        attempted_paths.append(f"Executable directory path: {exe_path}")
    else:
        attempted_paths.append("Not in frozen environment")
    
    # Method 2: Standard development path
    main_file = Path(__file__).resolve()
    project_root = main_file.parent.parent.parent.parent
    dev_path = project_root / "world_building_packages"
    possible_paths.append(dev_path)
    attempted_paths.append(f"Development path: {dev_path}")
    
    # Method 3: Legacy method
    legacy_path = Path(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "world_building_packages"
    ))
    possible_paths.append(legacy_path)
    attempted_paths.append(f"Legacy path: {legacy_path}")
    
    # Method 4: Current working directory
    cwd_path = Path.cwd() / "world_building_packages"
    possible_paths.append(cwd_path)
    attempted_paths.append(f"Current working directory path: {cwd_path}")
    
    # Method 5: Script directory
    if sys.argv and sys.argv[0]:
        script_dir = Path(sys.argv[0]).parent.resolve()
        script_path = script_dir / "world_building_packages"
        possible_paths.append(script_path)
        attempted_paths.append(f"Script directory path: {script_path}")
    
    # Add system info for debugging
    attempted_paths.append(f"sys.executable: {sys.executable}")
    attempted_paths.append(f"sys.argv[0]: {sys.argv[0] if sys.argv else 'None'}")
    attempted_paths.append(f"__file__: {__file__}")
    attempted_paths.append(f"Current working directory: {Path.cwd()}")
    
    # Check each possible path
    for path in possible_paths:
        attempted_paths.append(f"Checking path: {path} - exists: {path.exists()}, is_dir: {path.is_dir() if path.exists() else 'N/A'}")
        if path.exists() and path.is_dir():
            return str(path), attempted_paths
    
    return None, attempted_paths


def debug_world_building_packages() -> str:
    """
    Generate a comprehensive debug report for world_building_packages location issues.
    
    Returns:
        str: Debug information as a formatted string
    """
    found_path, attempted_paths = get_world_building_packages_path_debug()
    
    debug_info = []
    debug_info.append("=== World Building Packages Debug Report ===")
    debug_info.append(f"Found path: {found_path}")
    debug_info.append("")
    debug_info.append("Attempted paths and system info:")
    
    for i, path_info in enumerate(attempted_paths, 1):
        debug_info.append(f"  {i}. {path_info}")
    
    return "\n".join(debug_info)