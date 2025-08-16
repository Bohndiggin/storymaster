#!/usr/bin/env python3
"""
Qt6 Bundle Validation Script for Windows

Tests whether PyQt6 is properly bundled and can be imported in a PyInstaller executable.
This script can be run standalone or as part of the build validation process.
"""

import os
import sys
import traceback
from pathlib import Path


def print_environment_info():
    """Print environment and system information"""
    print("=" * 60)
    print("Qt6 Bundle Validation Test")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Frozen (PyInstaller): {getattr(sys, 'frozen', False)}")
    
    if hasattr(sys, '_MEIPASS'):
        print(f"Bundle directory: {sys._MEIPASS}")
    
    print("\nEnvironment variables:")
    qt_vars = ['QT_PLUGIN_PATH', 'QT_QPA_PLATFORM_PLUGIN_PATH', 'QT_QPA_PLATFORM', 'PATH']
    for var in qt_vars:
        value = os.environ.get(var, 'Not set')
        if var == 'PATH' and len(value) > 100:
            value = value[:100] + "... (truncated)"
        print(f"  {var}: {value}")
    print()


def test_basic_imports():
    """Test basic PyQt6 imports"""
    print("[TEST] Basic PyQt6 imports...")
    
    try:
        import PySide6
        print(f"✓ PyQt6 imported successfully (version: {PyQt6.__version__})")
        print(f"  Location: {PyQt6.__file__}")
    except ImportError as e:
        print(f"✗ Failed to import PySide6: {e}")
        return False
    
    try:
        from PySide6 import QtCore
        print(f"✓ QtCore imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import QtCore: {e}")
        return False
    
    try:
        from PySide6 import QtGui
        print(f"✓ QtGui imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import QtGui: {e}")
        return False
    
    try:
        from PySide6 import QtWidgets
        print(f"✓ QtWidgets imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import QtWidgets: {e}")
        return False
    
    return True


def test_qt_application():
    """Test creating a Qt application (without showing GUI)"""
    print("\n[TEST] Qt Application creation...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        
        # Create application without showing GUI
        app = QApplication([])
        print("✓ QApplication created successfully")
        
        # Test that the application can process events
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(100)  # Quit after 100ms
        
        app.exec()
        print("✓ QApplication event loop executed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create Qt application: {e}")
        print(f"   Error type: {type(e).__name__}")
        traceback.print_exc()
        return False


def test_bundle_files():
    """Test if required Qt6 files are present in the bundle"""
    print("\n[TEST] Bundle file validation...")
    
    if not hasattr(sys, '_MEIPASS'):
        print("  Skipping - not running in PyInstaller bundle")
        return True
    
    bundle_dir = Path(sys._MEIPASS)
    print(f"  Bundle directory: {bundle_dir}")
    
    # Check for Qt6 DLLs
    qt_dlls = list(bundle_dir.glob("Qt6*.dll"))
    if qt_dlls:
        print(f"✓ Found {len(qt_dlls)} Qt6 DLLs")
        for dll in sorted(qt_dlls)[:5]:  # Show first 5
            print(f"    - {dll.name}")
        if len(qt_dlls) > 5:
            print(f"    ... and {len(qt_dlls) - 5} more")
    else:
        print("✗ No Qt6 DLLs found in bundle")
        return False
    
    # Check for platform plugins
    platform_paths = [
        bundle_dir / "PyQt6" / "Qt6" / "plugins" / "platforms",
        bundle_dir / "plugins" / "platforms",
        bundle_dir / "platforms"
    ]
    
    platform_found = False
    for platform_path in platform_paths:
        if platform_path.exists():
            qwindows = platform_path / "qwindows.dll"
            if qwindows.exists():
                print(f"✓ Found platform plugin: {qwindows}")
                platform_found = True
                break
    
    if not platform_found:
        print("✗ qwindows.dll platform plugin not found")
        print("   Available paths checked:")
        for path in platform_paths:
            print(f"     - {path} (exists: {path.exists()})")
        return False
    
    # Check for Visual C++ runtime
    vc_dlls = ['msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll']
    found_vc = []
    for vc_dll in vc_dlls:
        if (bundle_dir / vc_dll).exists():
            found_vc.append(vc_dll)
    
    if found_vc:
        print(f"✓ Found VC++ runtime DLLs: {', '.join(found_vc)}")
    else:
        print("⚠ No VC++ runtime DLLs found in bundle (may be available from system)")
    
    return True


def test_simple_widget():
    """Test creating a simple widget (without showing it)"""
    print("\n[TEST] Simple widget creation...")
    
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
        
        # Create application if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create a simple widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Test Label")
        layout.addWidget(label)
        
        print("✓ Simple widget created successfully")
        print(f"  Widget size: {widget.size().width()}x{widget.size().height()}")
        print(f"  Label text: {label.text()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create simple widget: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all Qt6 validation tests"""
    print_environment_info()
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Bundle Files", test_bundle_files),
        ("Qt Application", test_qt_application),
        ("Simple Widget", test_simple_widget),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Qt6 bundle tests passed!")
        print("   The application should work on target Windows systems")
    else:
        print("❌ Some tests failed")
        print("   The application may not work properly on target systems")
        print("   Check the error messages above for troubleshooting")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)