"""
Test suite for utility functions and helper classes
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QApplication


class TestGeometryUtilities:
    """Test geometry-related utility functions"""

    def test_point_distance_calculation(self, qapp):
        """Test calculating distance between two points"""
        def calculate_distance(point1, point2):
            """Calculate Euclidean distance between two QPointF objects"""
            dx = point2.x() - point1.x()
            dy = point2.y() - point1.y()
            return (dx * dx + dy * dy) ** 0.5
        
        p1 = QPointF(0, 0)
        p2 = QPointF(3, 4)
        
        distance = calculate_distance(p1, p2)
        assert abs(distance - 5.0) < 0.001  # 3-4-5 triangle

    def test_point_in_rectangle(self, qapp):
        """Test checking if a point is inside a rectangle"""
        def point_in_rect(point, rect):
            """Check if point is inside rectangle"""
            return rect.contains(point)
        
        rect = QRectF(10, 10, 100, 100)  # x, y, width, height
        
        inside_point = QPointF(50, 50)
        outside_point = QPointF(5, 5)
        edge_point = QPointF(10, 10)
        
        assert point_in_rect(inside_point, rect)
        assert not point_in_rect(outside_point, rect)
        assert point_in_rect(edge_point, rect)

    def test_rectangle_intersection(self, qapp):
        """Test rectangle intersection calculations"""
        rect1 = QRectF(0, 0, 50, 50)
        rect2 = QRectF(25, 25, 50, 50)
        rect3 = QRectF(100, 100, 50, 50)
        
        # Test intersection
        assert rect1.intersects(rect2)
        assert not rect1.intersects(rect3)
        
        # Test intersection area
        intersection = rect1.intersected(rect2)
        assert intersection.width() == 25
        assert intersection.height() == 25

    def test_bounding_box_calculation(self, qapp):
        """Test calculating bounding box for multiple points"""
        def calculate_bounding_box(points):
            """Calculate bounding box for a list of points"""
            if not points:
                return QRectF()
            
            min_x = min(p.x() for p in points)
            max_x = max(p.x() for p in points)
            min_y = min(p.y() for p in points)
            max_y = max(p.y() for p in points)
            
            return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        
        points = [
            QPointF(10, 20),
            QPointF(50, 10),
            QPointF(30, 60),
            QPointF(5, 30)
        ]
        
        bbox = calculate_bounding_box(points)
        assert bbox.x() == 5
        assert bbox.y() == 10
        assert bbox.width() == 45  # 50 - 5
        assert bbox.height() == 50  # 60 - 10


class TestStringUtilities:
    """Test string manipulation utilities"""

    def test_string_validation(self):
        """Test string validation functions"""
        def is_valid_name(name):
            """Validate name strings"""
            if not name or not isinstance(name, str):
                return False
            name = name.strip()
            return len(name) >= 3 and len(name) <= 50 and name.isalnum()
        
        # Test valid names
        assert is_valid_name("TestName")
        assert is_valid_name("Name123")
        assert is_valid_name("ABC")
        
        # Test invalid names
        assert not is_valid_name("")
        assert not is_valid_name("Ab")  # Too short
        assert not is_valid_name("A" * 51)  # Too long
        assert not is_valid_name("Name with spaces")
        assert not is_valid_name("Name-with-dashes")
        assert not is_valid_name(None)
        assert not is_valid_name(123)

    def test_string_truncation(self):
        """Test string truncation with ellipsis"""
        def truncate_string(text, max_length, ellipsis="..."):
            """Truncate string to max_length, adding ellipsis if needed"""
            if not text or len(text) <= max_length:
                return text
            return text[:max_length - len(ellipsis)] + ellipsis
        
        long_text = "This is a very long string that needs to be truncated"
        
        # Test truncation
        short = truncate_string(long_text, 20)
        assert len(short) == 20
        assert short.endswith("...")
        
        # Test no truncation needed
        short_text = "Short"
        assert truncate_string(short_text, 20) == short_text
        
        # Test empty string
        assert truncate_string("", 10) == ""
        assert truncate_string(None, 10) is None

    def test_string_sanitization(self):
        """Test string sanitization for file names"""
        def sanitize_filename(filename):
            """Sanitize string for use as filename"""
            if not filename:
                return "untitled"
            
            # Remove invalid characters
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, '_')
            
            # Trim whitespace and dots
            filename = filename.strip(' .')
            
            # Ensure not empty
            if not filename:
                return "untitled"
            
            return filename
        
        # Test sanitization
        assert sanitize_filename("My Story: The Beginning") == "My Story_ The Beginning"
        assert sanitize_filename("File/Path\\Name") == "File_Path_Name"
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"
        assert sanitize_filename("...") == "untitled"
        assert sanitize_filename("Valid_Name") == "Valid_Name"

    def test_string_formatting(self):
        """Test string formatting utilities"""
        def format_timestamp(dt=None):
            """Format datetime for display"""
            if dt is None:
                dt = datetime.now()
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        
        def format_file_size(size_bytes):
            """Format file size in human-readable format"""
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
        
        # Test timestamp formatting
        test_dt = datetime(2023, 12, 25, 14, 30, 45)
        assert format_timestamp(test_dt) == "2023-12-25 14:30:45"
        
        # Test file size formatting
        assert format_file_size(512) == "512 B"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(2097152) == "2.0 MB"
        assert format_file_size(1073741824) == "1.0 GB"


class TestFileUtilities:
    """Test file handling utilities"""

    def test_safe_file_operations(self):
        """Test safe file operations with error handling"""
        def safe_read_file(filepath):
            """Safely read file contents"""
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return {"success": True, "content": f.read()}
            except FileNotFoundError:
                return {"success": False, "error": "File not found"}
            except PermissionError:
                return {"success": False, "error": "Permission denied"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        def safe_write_file(filepath, content):
            """Safely write content to file"""
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"success": True}
            except PermissionError:
                return {"success": False, "error": "Permission denied"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Test with temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write("test content")
            tmp_path = tmp.name
        
        try:
            # Test reading existing file
            result = safe_read_file(tmp_path)
            assert result["success"]
            assert result["content"] == "test content"
            
            # Test reading non-existent file
            result = safe_read_file("/nonexistent/file.txt")
            assert not result["success"]
            assert "File not found" in result["error"]
            
            # Test writing to file
            result = safe_write_file(tmp_path, "new content")
            assert result["success"]
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_path_utilities(self):
        """Test path manipulation utilities"""
        def ensure_directory_exists(path):
            """Ensure directory exists, create if needed"""
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)
            return path.exists()
        
        def get_file_info(filepath):
            """Get file information"""
            path = Path(filepath)
            if not path.exists():
                return None
            
            return {
                "name": path.name,
                "stem": path.stem,
                "suffix": path.suffix,
                "size": path.stat().st_size,
                "is_file": path.is_file(),
                "is_dir": path.is_dir()
            }
        
        # Test directory creation
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_dir = Path(tmp_dir) / "test" / "nested" / "directory"
            assert ensure_directory_exists(test_dir)
            assert test_dir.exists()
            assert test_dir.is_dir()
        
        # Test file info
        with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
            tmp.write(b"test data")
            tmp.flush()
            
            info = get_file_info(tmp.name)
            assert info is not None
            assert info["suffix"] == ".db"
            assert info["size"] > 0
            assert info["is_file"]
            assert not info["is_dir"]

    def test_backup_file_naming(self):
        """Test backup file naming conventions"""
        def generate_backup_filename(original_path, timestamp=None):
            """Generate backup filename with timestamp"""
            path = Path(original_path)
            if timestamp is None:
                timestamp = datetime.now()
            
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            backup_name = f"{path.stem}_{timestamp_str}{path.suffix}"
            return path.parent / "backups" / backup_name
        
        def parse_backup_filename(backup_path):
            """Parse timestamp from backup filename"""
            path = Path(backup_path)
            name_parts = path.stem.split('_')
            
            if len(name_parts) >= 3:
                date_part = name_parts[-2]
                time_part = name_parts[-1]
                timestamp_str = f"{date_part}_{time_part}"
                
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    original_name = '_'.join(name_parts[:-2])
                    return {"timestamp": timestamp, "original_name": original_name}
                except ValueError:
                    pass
            
            return None
        
        # Test backup filename generation
        original = "/path/to/database.db"
        test_time = datetime(2023, 12, 25, 14, 30, 45)
        
        backup_path = generate_backup_filename(original, test_time)
        assert backup_path.name == "database_20231225_143045.db"
        assert backup_path.parent.name == "backups"
        
        # Test parsing backup filename
        parsed = parse_backup_filename(backup_path)
        assert parsed is not None
        assert parsed["timestamp"] == test_time
        assert parsed["original_name"] == "database"


class TestDataUtilities:
    """Test data manipulation utilities"""

    def test_list_utilities(self):
        """Test list manipulation functions"""
        def safe_get_item(items, index, default=None):
            """Safely get item from list by index"""
            try:
                return items[index]
            except (IndexError, TypeError):
                return default
        
        def remove_duplicates(items, key_func=None):
            """Remove duplicates from list, optionally using key function"""
            if key_func is None:
                return list(dict.fromkeys(items))  # Preserves order
            
            seen = set()
            result = []
            for item in items:
                key = key_func(item)
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result
        
        def chunk_list(items, chunk_size):
            """Split list into chunks of specified size"""
            for i in range(0, len(items), chunk_size):
                yield items[i:i + chunk_size]
        
        # Test safe item access
        test_list = [1, 2, 3]
        assert safe_get_item(test_list, 1) == 2
        assert safe_get_item(test_list, 10) is None
        assert safe_get_item(test_list, 10, "default") == "default"
        assert safe_get_item(None, 0, "default") == "default"
        
        # Test duplicate removal
        duplicates = [1, 2, 2, 3, 1, 4]
        unique = remove_duplicates(duplicates)
        assert unique == [1, 2, 3, 4]
        
        # Test duplicate removal with key function
        objects = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}, {"id": 1, "name": "C"}]
        unique_objects = remove_duplicates(objects, key_func=lambda x: x["id"])
        assert len(unique_objects) == 2
        assert unique_objects[0]["id"] == 1
        assert unique_objects[1]["id"] == 2
        
        # Test list chunking
        long_list = list(range(10))
        chunks = list(chunk_list(long_list, 3))
        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[1] == [3, 4, 5]
        assert chunks[3] == [9]  # Last chunk might be smaller

    def test_dictionary_utilities(self):
        """Test dictionary manipulation functions"""
        def deep_merge(dict1, dict2):
            """Deep merge two dictionaries"""
            result = dict1.copy()
            for key, value in dict2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        def get_nested_value(data, keys, default=None):
            """Get nested value from dictionary using key path"""
            current = data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            return current
        
        def flatten_dict(data, separator='.', prefix=''):
            """Flatten nested dictionary"""
            result = {}
            for key, value in data.items():
                new_key = f"{prefix}{separator}{key}" if prefix else key
                if isinstance(value, dict):
                    result.update(flatten_dict(value, separator, new_key))
                else:
                    result[new_key] = value
            return result
        
        # Test deep merge
        dict1 = {"a": 1, "b": {"c": 2, "d": 3}}
        dict2 = {"b": {"d": 4, "e": 5}, "f": 6}
        
        merged = deep_merge(dict1, dict2)
        assert merged["a"] == 1
        assert merged["b"]["c"] == 2
        assert merged["b"]["d"] == 4  # Overwritten
        assert merged["b"]["e"] == 5  # Added
        assert merged["f"] == 6
        
        # Test nested value access
        nested = {"user": {"profile": {"name": "Test User"}}}
        assert get_nested_value(nested, ["user", "profile", "name"]) == "Test User"
        assert get_nested_value(nested, ["user", "settings", "theme"]) is None
        assert get_nested_value(nested, ["user", "settings", "theme"], "default") == "default"
        
        # Test dictionary flattening
        nested = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        flattened = flatten_dict(nested)
        assert flattened["a"] == 1
        assert flattened["b.c"] == 2
        assert flattened["b.d.e"] == 3

    def test_validation_utilities(self):
        """Test data validation functions"""
        def validate_range(value, min_val=None, max_val=None):
            """Validate numeric value is within range"""
            try:
                num_value = float(value)
                if min_val is not None and num_value < min_val:
                    return False, f"Value must be at least {min_val}"
                if max_val is not None and num_value > max_val:
                    return False, f"Value must be at most {max_val}"
                return True, "Valid"
            except (ValueError, TypeError):
                return False, "Invalid number"
        
        def validate_required_fields(data, required_fields):
            """Validate that required fields are present and not empty"""
            missing = []
            empty = []
            
            for field in required_fields:
                if field not in data:
                    missing.append(field)
                elif not str(data[field]).strip():
                    empty.append(field)
            
            if missing:
                return False, f"Missing required fields: {', '.join(missing)}"
            if empty:
                return False, f"Empty required fields: {', '.join(empty)}"
            
            return True, "Valid"
        
        # Test range validation
        assert validate_range("5", 0, 10)[0]
        assert not validate_range("-1", 0, 10)[0]
        assert not validate_range("15", 0, 10)[0]
        assert not validate_range("abc")[0]
        
        # Test required fields validation
        data = {"name": "Test", "description": "Test desc", "empty_field": ""}
        valid, msg = validate_required_fields(data, ["name", "description"])
        assert valid
        
        valid, msg = validate_required_fields(data, ["name", "missing_field"])
        assert not valid
        assert "Missing required fields" in msg
        
        valid, msg = validate_required_fields(data, ["name", "empty_field"])
        assert not valid
        assert "Empty required fields" in msg