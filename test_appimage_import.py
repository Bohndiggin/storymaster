#!/usr/bin/env python3
"""
Test script to debug Character Arc Types import in AppImage environment
"""

import sys
import os
import traceback
from pathlib import Path


def test_import():
    """Test the Character Arc Types import functionality"""

    print("=== Testing Character Arc Types Import ===")
    print(f"Python version: {sys.version}")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"Current working directory: {os.getcwd()}")
    print()

    # Test 1: Check if we can import the dialog module
    try:
        sys.path.insert(0, ".")
        from storymaster.view.common.import_lore_packages_dialog import (
            import_world_building_package,
        )

        print("✅ Successfully imported import_world_building_package")
    except Exception as e:
        print(f"❌ Failed to import import_world_building_package: {e}")
        traceback.print_exc()
        return

    # Test 2: Check world_building_packages path
    try:
        from storymaster.view.common.package_utils import (
            get_world_building_packages_path,
        )

        packages_path = get_world_building_packages_path()
        print(f"📁 World building packages path: {packages_path}")

        if packages_path and os.path.exists(packages_path):
            arc_types_file = os.path.join(packages_path, "character_arc_types.json")
            print(
                f"📄 Character arc types file exists: {os.path.exists(arc_types_file)}"
            )
            if os.path.exists(arc_types_file):
                print(f"📄 File path: {arc_types_file}")
                # Check file size
                file_size = os.path.getsize(arc_types_file)
                print(f"📊 File size: {file_size} bytes")
        else:
            print("❌ World building packages path not found")
            return
    except Exception as e:
        print(f"❌ Error checking packages path: {e}")
        traceback.print_exc()
        return

    # Test 3: Test model creation
    try:
        from storymaster.model.common.common_model import BaseModel
        from sqlalchemy.orm import Session
        from storymaster.model.database import schema

        print("🔧 Creating test model...")
        model = BaseModel(user_id=1)
        print("✅ Model created successfully")

        # Create a test setting
        with Session(model.engine) as session:
            existing_setting = (
                session.query(schema.Setting)
                .filter_by(name="AppImage Test Setting")
                .first()
            )
            if not existing_setting:
                test_setting = schema.Setting(
                    name="AppImage Test Setting",
                    description="Test setting for AppImage import",
                    user_id=1,
                )
                session.add(test_setting)
                session.commit()
                setting_id = test_setting.id
                print(f"✅ Created test setting with ID: {setting_id}")
            else:
                setting_id = existing_setting.id
                print(f"✅ Using existing test setting with ID: {setting_id}")

    except Exception as e:
        print(f"❌ Error creating model/setting: {e}")
        traceback.print_exc()
        return

    # Test 4: Test the actual import
    try:
        print("🚀 Testing Character Arc Types import...")
        arc_types_file = os.path.join(packages_path, "character_arc_types.json")
        result = import_world_building_package(arc_types_file, setting_id)

        if result:
            print("✅ Character Arc Types import successful!")
        else:
            print("❌ Character Arc Types import failed!")

    except Exception as e:
        print(f"❌ Exception during import: {e}")
        traceback.print_exc()

    print("=== Test Complete ===")


if __name__ == "__main__":
    test_import()
