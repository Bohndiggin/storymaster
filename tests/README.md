# Storymaster Test Suite

This directory contains tests for the Storymaster application, with a focus on the Blender-style node connection system.

## Test Structure

### Core Test Files

- **`test_node_system.py`** - Main pytest-compatible tests for node connection system
- **`run_tests.py`** - Standalone test runner (no pytest required)
- **`conftest.py`** - Simple pytest configuration for GUI tests

### Specialized Test Directories

- **`controller/litographer/`** - Detailed tests for node controller functionality
  - `test_node_connections.py` - Connection point behavior
  - `test_node_positioning.py` - Node positioning and scene management
  - `test_node_type_changes.py` - Node type change functionality
  - `test_node_ui_only.py` - UI-only conceptual tests
  - `README.md` - Detailed documentation for litographer tests

## Running Tests

### Quick Test (Recommended)
```bash
python run_tests.py
```
This runs a comprehensive test suite without database dependencies.

### Pytest
```bash
pytest tests/test_node_system.py -v
```
Runs the main test suite using pytest.

### All Tests
```bash
pytest tests/ -v
```
Runs all available tests (may require database setup for some tests).

## Test Coverage

The test suite verifies the following Blender-style node system features:

### ✅ Core Functionality
- **Visual connection points** (green input, red output) 
- **Connection point positioning** mathematics
- **Dynamic updates** during node movement
- **Position preservation** during node type changes
- **Scene management** and redraw stability

### ✅ Fixed Issues
1. **Connection points jumping to origin** - Fixed by proper node creation in `load_and_draw_nodes()`
2. **Node type changes losing position** - Fixed by `get_node_ui_position()` method  
3. **Connections not updating during movement** - Fixed by `update_all_connections()` integration
4. **Yellow indicator line from wrong position** - Fixed by proper scene positioning

### ✅ Integration Testing
- Node system component imports
- Mock object creation for testing
- Connection point method functionality
- Graphics scene integration

## Test Design Philosophy

The tests are designed to be:

- **Lightweight** - Core tests don't require database setup
- **Fast** - Most tests run in under 1 second
- **Isolated** - Tests don't depend on external state
- **Comprehensive** - Cover both concepts and implementation
- **Maintainable** - Clear structure and documentation

## Test Categories

### 1. Conceptual Tests
Test the mathematical and logical foundations:
- Position tracking algorithms
- Connection point calculations
- Movement and transformation logic

### 2. Integration Tests  
Test interaction with actual Qt components:
- QGraphicsScene management
- QPointF positioning
- Node item creation and behavior

### 3. Fix Verification Tests
Verify specific bug fixes:
- Node type change position preservation
- Connection point stability during redraws
- Proper UI state tracking

## Dependencies

### Required
- PyQt6 (for GUI components)
- Python 3.8+ 

### Optional
- pytest (for pytest runner)
- SQLAlchemy (for database-dependent tests)

## Development Workflow

1. **Quick verification**: `python run_tests.py`
2. **Detailed testing**: `pytest tests/test_node_system.py -v`
3. **Full test suite**: `pytest tests/ -v` (if database is set up)

The test suite ensures the Blender-style node connection system remains stable and functional across code changes.