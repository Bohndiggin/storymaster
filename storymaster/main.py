"""
Storymaster - Main Application Entry Point
"""

import os
import sys
from pathlib import Path

# Initialize Qt plugin paths for bundled executable
if getattr(sys, "frozen", False):
    # Running in bundled mode
    bundle_dir = Path(sys._MEIPASS)  # type: ignore

    # Windows-specific DLL loading fix
    if sys.platform.startswith("win"):
        # Add bundle directory to DLL search path for Windows
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(str(bundle_dir))  # type: ignore
            except (OSError, AttributeError):
                pass

        # Fallback: prepend bundle directory to PATH
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{bundle_dir}{os.pathsep}{current_path}"

    # Set Qt plugin paths
    qt_plugin_paths = [bundle_dir / "PySide6" / "Qt6" / "plugins", bundle_dir / "plugins"]

    for plugin_path in qt_plugin_paths:
        if plugin_path.exists():
            current_path = os.environ.get("QT_PLUGIN_PATH", "")
            if current_path:
                os.environ["QT_PLUGIN_PATH"] = f"{current_path}{os.pathsep}{plugin_path}"
            else:
                os.environ["QT_PLUGIN_PATH"] = str(plugin_path)

    # Set platform plugin path specifically
    platform_path = bundle_dir / "PySide6" / "Qt6" / "plugins" / "platforms"
    if platform_path.exists():
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platform_path)

from PySide6.QtWidgets import QApplication
import datetime

current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir.resolve()))

from storymaster.controller.common.main_page_controller import MainWindowController
from storymaster.controller.common.user_startup import get_startup_user_id
from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.common_view import MainView
from storymaster.sync_server.server_manager import start_sync_server, stop_sync_server


def debug_environment():
    """Debug the environment for troubleshooting AppImage issues"""
    print("=== Storymaster Environment Debug ===")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"sys.executable: {sys.executable}")
    print(f"sys.argv[0]: {sys.argv[0] if sys.argv else 'None'}")
    print(f"__file__: {__file__}")
    print(f"Current working directory: {Path.cwd()}")

    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            print(f"PyInstaller bundle dir: {sys._MEIPASS}")  # type: ignore
            bundle_dir = Path(sys._MEIPASS)  # type: ignore
            wb_path = bundle_dir / "world_building_packages"
            print(f"Bundle world_building_packages exists: {wb_path.exists()}")
            if wb_path.exists():
                print(f"Bundle world_building_packages files: {list(wb_path.glob('*.json'))}")

    # Test our utility function
    try:
        from storymaster.view.common.package_utils import (
            get_world_building_packages_path,
        )

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
        import sqlite3

        from sqlalchemy import create_engine, inspect

        # Get database URL from environment or use default
        db_url = os.getenv("DATABASE_CONNECTION")
        if not db_url:
            # Use the same path as seed.py
            db_path = os.path.expanduser("~/.local/share/storymaster/storymaster.db")
            db_url = f"sqlite:///{db_path}"
        elif not db_url.startswith("sqlite:///") and not os.path.isabs(
            db_url.replace("sqlite:///", "")
        ):
            # Make relative SQLite paths absolute
            db_file = db_url.replace("sqlite:///", "")
            db_path = Path(__file__).parent.parent / db_file
            db_url = f"sqlite:///{db_path}"

        engine = create_engine(db_url)
        inspector = inspect(engine)

        # Check for arc_type constraint migration
        needs_arc_type_migration = False
        if "arc_type" in inspector.get_table_names():
            # Check if old unique constraint exists using raw SQL
            conn = sqlite3.connect(db_url.replace("sqlite:///", ""))
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='arc_type'")
            result = cursor.fetchone()
            if result:
                create_statement = result[0]
                # Check for old constraint (UNIQUE without composite constraint name)
                if (
                    "UNIQUE" in create_statement
                    and "uq_arc_type_name_setting" not in create_statement
                ):
                    needs_arc_type_migration = True
            conn.close()

        if needs_arc_type_migration:
            print("🔄 Database needs arc_type constraint migration...")
            print("   (Fixing constraint to allow same arc type in different settings)")

            # Import and run arc_type migration
            migration_script = (
                Path(__file__).parent.parent / "scripts" / "migrate_arc_type_constraint.py"
            )
            if migration_script.exists():
                # Run migration script
                import subprocess

                result = subprocess.run(
                    [sys.executable, str(migration_script)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("✅ Arc type migration completed successfully!")
                else:
                    print(f"❌ Arc type migration failed: {result.stderr}")

        # Check for note_type case migration
        needs_note_type_migration = False
        if "litography_notes" in inspector.get_table_names():
            # Check if there are uppercase note_type values using raw SQL
            conn = sqlite3.connect(db_url.replace("sqlite:///", ""))
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM litography_notes
                WHERE note_type != LOWER(note_type)
            """
            )
            uppercase_count = cursor.fetchone()[0]
            conn.close()
            if uppercase_count > 0:
                needs_note_type_migration = True

        if needs_note_type_migration:
            print("🔄 Database needs note_type case migration...")
            print("   (Fixing uppercase note_type values to match enum)")

            # Import and run note_type migration
            migration_script = (
                Path(__file__).parent.parent / "scripts" / "migrate_note_type_case.py"
            )
            if migration_script.exists():
                # Run migration script
                import subprocess

                result = subprocess.run(
                    [sys.executable, str(migration_script)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("✅ Note type migration completed successfully!")
                else:
                    print(f"❌ Note type migration failed: {result.stderr}")

        # Check for plot_section_type capitalization migration
        needs_plot_section_migration = False
        if "litography_plot_section" in inspector.get_table_names():
            # Check if there are old capitalization values using raw SQL
            conn = sqlite3.connect(db_url.replace("sqlite:///", ""))
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM litography_plot_section
                WHERE plot_section_type IN (
                    'Tension lowers',
                    'Tension sustains',
                    'Increases tension',
                    'Singular moment'
                )
            """
            )
            old_values_count = cursor.fetchone()[0]
            conn.close()
            if old_values_count > 0:
                needs_plot_section_migration = True

        if needs_plot_section_migration:
            print("🔄 Database needs plot_section_type capitalization migration...")
            print("   (Updating plot section types to match PlotSectionType enum)")

            # Import and run plot_section_type migration
            migration_script = (
                Path(__file__).parent.parent / "scripts" / "migrate_plot_section_type.py"
            )
            if migration_script.exists():
                # Run migration script
                import subprocess

                result = subprocess.run(
                    [sys.executable, str(migration_script)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("✅ Plot section type migration completed successfully!")
                else:
                    print(f"❌ Plot section type migration failed: {result.stderr}")

        # Check if migration is needed by looking for new fields in faction_members
        needs_relationship_migration = False
        if "faction_members" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("faction_members")]
            if "description" not in columns:
                needs_relationship_migration = True

        if needs_relationship_migration:
            print("🔄 Database needs relationship migration...")

            # Import and run migration
            migration_script = Path(__file__).parent.parent / "scripts" / "migrate_relationships.py"
            if migration_script.exists():
                # Run migration script
                import subprocess

                result = subprocess.run(
                    [sys.executable, str(migration_script)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("✅ Migration completed successfully!")
                    print("🔄 Please restart the application to use the new relationship fields.")
                    sys.exit(0)  # Force restart to reload schema
                else:
                    print(f"❌ Migration failed: {result.stderr}")

        # Check for sync fields migration
        needs_sync_migration = False
        if "user" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("user")]
            if "created_at" not in columns:
                needs_sync_migration = True

        if needs_sync_migration:
            print("🔄 Database needs sync fields migration...")
            print("   (Adding timestamp tracking for mobile sync)")

            # Import and run sync migration
            migration_script = Path(__file__).parent.parent / "scripts" / "migrate_sync_fields.py"
            if migration_script.exists():
                # Run migration script
                import subprocess

                result = subprocess.run(
                    [sys.executable, str(migration_script)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("✅ Sync migration completed successfully!")
                else:
                    print(f"❌ Sync migration failed: {result.stderr}")

    except Exception as e:
        print(f"⚠️  Migration check failed: {e}")
        # Continue anyway - don't block startup

def main():
    """Main entry point for Storymaster application"""
    # Check for debug flag
    if "--debug-packages" in sys.argv:
        debug_environment()
        # Also test the utility directly
        try:
            from storymaster.view.common.package_utils import (
                debug_world_building_packages,
            )

            print(debug_world_building_packages())
        except Exception as e:
            print(f"Error running package debug: {e}")
        sys.exit(0)

    # Enable debug output for AppImage troubleshooting (can be removed in production)
    if getattr(sys, "frozen", False):
        debug_environment()

    app = QApplication(sys.argv)

    # Check and run database migrations if needed
    check_and_run_migrations()

    # Start sync server in background
    print("\n📱 Starting mobile sync server...")
    sync_server_started = start_sync_server(host="0.0.0.0", port=8765)
    if sync_server_started:
        print("✅ Sync server is running!")
        print("📲 Scan QR code at: http://localhost:8765/api/pair/qr-image")
    else:
        print("⚠️  Sync server failed to start (app will continue without sync)")

    # Get the user ID to use for startup (creates user if none exist)
    user_id = get_startup_user_id()

    view = MainView()
    model = BaseModel(user_id)
    controller = MainWindowController(view, model)
    view.controller = controller  # Set controller reference for cleanup
    view.show()

    try:
        exit_code = app.exec()
    finally:
        # Ensure sync server is stopped on exit
        print("\n🛑 Shutting down sync server...")
        stop_sync_server()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
