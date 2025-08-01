"""Storio's main file"""

import os
import sys
from pathlib import Path

# Initialize Qt plugin paths for bundled executable
if getattr(sys, 'frozen', False):
    # Running in bundled mode
    bundle_dir = Path(sys._MEIPASS)
    
    # Windows-specific DLL loading fix
    if sys.platform.startswith('win'):
        # Add bundle directory to DLL search path for Windows
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(str(bundle_dir))
            except (OSError, AttributeError):
                pass
        
        # Fallback: prepend bundle directory to PATH
        current_path = os.environ.get('PATH', '')
        os.environ['PATH'] = f"{bundle_dir}{os.pathsep}{current_path}"
    
    # Set Qt plugin paths
    qt_plugin_paths = [
        bundle_dir / 'PyQt6' / 'Qt6' / 'plugins',
        bundle_dir / 'plugins'
    ]
    
    for plugin_path in qt_plugin_paths:
        if plugin_path.exists():
            current_path = os.environ.get('QT_PLUGIN_PATH', '')
            if current_path:
                os.environ['QT_PLUGIN_PATH'] = f"{current_path}{os.pathsep}{plugin_path}"
            else:
                os.environ['QT_PLUGIN_PATH'] = str(plugin_path)
    
    # Set platform plugin path specifically
    platform_path = bundle_dir / 'PyQt6' / 'Qt6' / 'plugins' / 'platforms'
    if platform_path.exists():
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(platform_path)

from PyQt6.QtWidgets import QApplication

current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir.resolve()))

from storymaster.controller.common.main_page_controller import MainWindowController
from storymaster.controller.common.user_startup import get_startup_user_id
from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.common_view import MainView


def debug_environment():
    """Debug the environment for troubleshooting AppImage issues"""
    print("=== Storymaster Environment Debug ===")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"sys.executable: {sys.executable}")
    print(f"sys.argv[0]: {sys.argv[0] if sys.argv else 'None'}")
    print(f"__file__: {__file__}")
    print(f"Current working directory: {Path.cwd()}")
    
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            print(f"PyInstaller bundle dir: {sys._MEIPASS}")
            bundle_dir = Path(sys._MEIPASS)
            wb_path = bundle_dir / "world_building_packages"
            print(f"Bundle world_building_packages exists: {wb_path.exists()}")
            if wb_path.exists():
                print(f"Bundle world_building_packages files: {list(wb_path.glob('*.json'))}")
    
    # Test our utility function
    try:
        from storymaster.view.common.package_utils import get_world_building_packages_path
        path = get_world_building_packages_path()
        print(f"Package utility found path: {path}")
    except ImportError as e:
        print(f"Failed to import package utilities: {e}")
    except Exception as e:
        print(f"Error testing package utilities: {e}")
    
    print("======================================")
    print()

def check_and_run_migrations():
    """Check if database migrations are needed and run them"""
    try:
        from sqlalchemy import create_engine, inspect
        
        # Get database URL from environment or use default
        db_url = os.getenv("DATABASE_CONNECTION")
        if not db_url:
            # Use the same path as seed.py
            db_path = os.path.expanduser('~/.local/share/storymaster/storymaster.db')
            db_url = f"sqlite:///{db_path}"
        elif not db_url.startswith("sqlite:///") and not os.path.isabs(db_url.replace("sqlite:///", "")):
            # Make relative SQLite paths absolute
            db_file = db_url.replace("sqlite:///", "")
            db_path = Path(__file__).parent.parent / db_file
            db_url = f"sqlite:///{db_path}"
        
        engine = create_engine(db_url)
        inspector = inspect(engine)
        
        # Check if migration is needed by looking for new fields in faction_members
        needs_migration = False
        if "faction_members" in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns("faction_members")]
            if "description" not in columns:
                needs_migration = True
        
        if needs_migration:
            print("🔄 Database needs relationship migration...")
            
            # Import and run migration
            migration_script = Path(__file__).parent.parent / "migrate_relationships.py"
            if migration_script.exists():
                # Run migration script
                import subprocess
                result = subprocess.run([sys.executable, str(migration_script)], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Migration completed successfully!")
                    print("🔄 Please restart the application to use the new relationship fields.")
                    sys.exit(0)  # Force restart to reload schema
                else:
                    print(f"❌ Migration failed: {result.stderr}")
                    
    except Exception as e:
        print(f"⚠️  Migration check failed: {e}")
        # Continue anyway - don't block startup


if __name__ == "__main__":
    # Check for debug flag
    if "--debug-packages" in sys.argv:
        debug_environment()
        # Also test the utility directly
        try:
            from storymaster.view.common.package_utils import debug_world_building_packages
            print(debug_world_building_packages())
        except Exception as e:
            print(f"Error running package debug: {e}")
        sys.exit(0)
    
    # Enable debug output for AppImage troubleshooting (can be removed in production)
    if getattr(sys, 'frozen', False):
        debug_environment()
    
    app = QApplication(sys.argv)

    # Check and run database migrations if needed
    check_and_run_migrations()

    # Get the user ID to use for startup (creates user if none exist)
    user_id = get_startup_user_id()

    view = MainView()
    model = BaseModel(user_id)
    controller = MainWindowController(view, model)
    view.show()

    sys.exit(app.exec())
