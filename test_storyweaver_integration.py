#!/usr/bin/env python3
"""
Test script to verify Storyweaver integration with Storymaster.
"""
import sys
from PySide6.QtWidgets import QApplication
from storymaster.model.common.common_model import BaseModel
from storymaster.view.storyweaver.storyweaver_widget import StoryweaverWidget

def test_storyweaver_widget():
    """Test that the Storyweaver widget can be instantiated."""
    app = QApplication(sys.argv)

    # Create model (use user_id=1 for testing)
    model = BaseModel(user_id=1)

    # Try to create widget
    try:
        widget = StoryweaverWidget(
            model=model,
            current_storyline_id=1,
            current_setting_id=1
        )
        print("✓ StoryweaverWidget created successfully")

        # Test entity list setting
        test_entities = [
            {"id": "actor_1", "name": "Gandalf", "type": "character"},
            {"id": "location_1", "name": "Rivendell", "type": "location"},
            {"id": "faction_1", "name": "Fellowship", "type": "faction"}
        ]

        widget.set_entity_list(test_entities)
        print("✓ Entity list set successfully")

        # Test entity search signal
        widget.entity_search_requested.emit("", 1, 1)
        print("✓ Entity search signal emitted successfully")

        # Test document creation
        widget.editor.set_text("# Test Document\n\nThis is a test with [[Gandalf|actor_1]]")
        print("✓ Editor text set successfully")

        # Cleanup
        widget.cleanup()
        print("✓ Widget cleanup successful")

        print("\n✓✓✓ All tests passed! Storyweaver integration is working.")
        return True

    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_storyweaver_widget()
    sys.exit(0 if success else 1)
