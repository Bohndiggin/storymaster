#!/usr/bin/env python3
"""
Test script to verify PyQt6 works in bundled executable
Run this to test if PyQt6 modules load correctly
"""

import sys
import os
from pathlib import Path


def test_pyqt_imports():
    """Test importing PyQt6 modules"""
    print("Testing PyQt6 imports...")

    try:
        print("  Importing PyQt6.QtCore...", end=" ")
        from PyQt6.QtCore import QApplication, QTimer, pyqtSignal

        print("✓")

        print("  Importing PyQt6.QtWidgets...", end=" ")
        from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout

        print("✓")

        print("  Importing PyQt6.QtGui...", end=" ")
        from PyQt6.QtGui import QFont, QPixmap, QPainter

        print("✓")

        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_qapplication():
    """Test creating QApplication"""
    print("Testing QApplication creation...")

    try:
        from PyQt6.QtWidgets import QApplication

        app = QApplication([])
        print("  QApplication created successfully ✓")
        app.quit()
        return True
    except Exception as e:
        print(f"  QApplication creation failed: {e}")
        return False


def test_widget_creation():
    """Test creating Qt widgets"""
    print("Testing widget creation...")

    try:
        from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

        app = QApplication([])

        # Create a simple widget
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("PyQt6 Bundle Test")
        layout.addWidget(label)
        widget.setLayout(layout)

        print("  Widgets created successfully ✓")
        app.quit()
        return True
    except Exception as e:
        print(f"  Widget creation failed: {e}")
        return False


def check_environment():
    """Check bundled environment"""
    print("Checking environment...")

    print(f"  Python executable: {sys.executable}")
    print(f"  Frozen: {getattr(sys, 'frozen', False)}")

    if getattr(sys, "frozen", False):
        print(f"  Bundle directory: {sys._MEIPASS}")
        bundle_path = Path(sys._MEIPASS)

        # Check for Qt plugins
        qt_plugin_paths = [
            bundle_path / "PyQt6" / "Qt6" / "plugins",
            bundle_path / "plugins",
        ]

        for plugin_path in qt_plugin_paths:
            if plugin_path.exists():
                print(f"  Qt plugins found: {plugin_path} ✓")
                platforms = plugin_path / "platforms"
                if platforms.exists():
                    platform_files = list(platforms.glob("*"))
                    print(f"  Platform plugins: {len(platform_files)} files")
            else:
                print(f"  Qt plugins missing: {plugin_path}")

    # Check environment variables
    qt_vars = ["QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_PLATFORM"]
    for var in qt_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")


def main():
    """Main test function"""
    print("=" * 50)
    print("PyQt6 Bundle Test")
    print("=" * 50)

    check_environment()
    print()

    tests = [
        ("Import Test", test_pyqt_imports),
        ("QApplication Test", test_qapplication),
        ("Widget Creation Test", test_widget_creation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        if test_func():
            passed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! PyQt6 bundle is working correctly.")
        return True
    else:
        print("❌ Some tests failed. PyQt6 bundle needs fixing.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
