# Litographer Controller Tests

This directory contains tests for the Blender-style node connection system implemented in the Litographer controller.

## Test Files

### `test_node_ui_only.py`
Tests the core UI concepts and mathematical foundations of the node connection system without database dependencies:
- Graphics scene creation
- QPointF positioning
- Connection point mathematics
- Position tracking concepts
- Node type change position preservation

### `test_node_connections.py` 
Tests the actual node connection functionality (requires full application setup):
- Connection point methods on all node types
- Connection point positioning and movement
- Parent-child relationship between nodes and connection points

### `test_node_positioning.py`
Tests node positioning and scene redraw functionality:
- Multiple node isolation
- Scene clear/redraw scenarios
- Real workflow simulation
- UI position tracking methods

### `test_node_type_changes.py`
Tests the node type change functionality:
- Position preservation during type changes
- UI position tracking methods
- Fallback behavior

## Running Tests

### Standalone UI Tests
For testing core concepts without database setup:
```bash
python test_standalone.py
```

### Full Pytest Suite
For comprehensive testing (requires database setup):
```bash
pytest tests/controller/litographer/ -v
```

## Test Coverage

These tests verify the following features of the Blender-style node system:

✅ **Visual connection points** (green input, red output) attached to node shapes  
✅ **Dynamic connection updates** during node movement  
✅ **Position preservation** when changing node types  
✅ **Scene redraw stability** - connection points don't jump to origin  
✅ **Multi-node isolation** - moving one node doesn't affect others  
✅ **Connection point mathematics** - proper left/right/center positioning  

## Key Fixes Tested

1. **Connection points jumping to origin** - Fixed by proper positioning in `load_and_draw_nodes()`
2. **Node type changes losing position** - Fixed by `get_node_ui_position()` method
3. **Connections not updating during movement** - Fixed by `update_all_connections()` calls
4. **Yellow indicator line from wrong position** - Fixed by proper scene positioning

## Test Dependencies

- PyQt6 (for UI components)
- pytest (for test framework)
- SQLAlchemy (for database tests - optional)

The UI-only tests can run without database setup, making them suitable for quick verification of core functionality.