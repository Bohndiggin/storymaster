#!/usr/bin/env python3
"""
Test that all build resources are available and valid
"""

from pathlib import Path
import sys


def test_icon_files():
    """Test that icon files exist and are valid"""
    print("Testing icon files...")

    assets_dir = Path("assets")
    if not assets_dir.exists():
        print("❌ assets/ directory not found")
        return False

    required_icons = [
        "storymaster_icon.ico",
        "storymaster_icon.svg",
        "storymaster_icon_16.png",
        "storymaster_icon_32.png",
        "storymaster_icon_64.png",
    ]

    all_good = True
    for icon_name in required_icons:
        icon_path = assets_dir / icon_name
        if icon_path.exists():
            size = icon_path.stat().st_size
            print(f"  ✓ {icon_name} ({size} bytes)")

            # Check if file is reasonable size
            if size < 100:
                print(f"    ⚠️  File seems too small")
                all_good = False
        else:
            print(f"  ❌ {icon_name} - MISSING")
            all_good = False

    return all_good


def test_version_info():
    """Test version info file"""
    print("Testing version info...")

    version_file = Path("version_info.py")
    if not version_file.exists():
        print("  ❌ version_info.py not found")
        return False

    try:
        # Try to import/compile the version info
        with open(version_file, "r") as f:
            content = f.read()

        # Check if it has the basic structure
        if "VSVersionInfo" in content:
            print("  ✓ version_info.py structure looks good")
        else:
            print("  ⚠️  version_info.py missing VSVersionInfo")

        # Try to compile it
        compile(content, str(version_file), "exec")
        print("  ✓ version_info.py compiles successfully")
        return True

    except Exception as e:
        print(f"  ❌ version_info.py error: {e}")
        return False


def test_spec_file():
    """Test spec file"""
    print("Testing spec file...")

    spec_file = Path("storymaster.spec")
    if not spec_file.exists():
        print("  ❌ storymaster.spec not found")
        return False

    try:
        with open(spec_file, "r") as f:
            content = f.read()

        # Check for key components
        checks = [
            ("Analysis", "Analysis(" in content),
            ("EXE", "EXE(" in content),
            ("Icon reference", "storymaster_icon.ico" in content),
            ("Project dir", "project_dir" in content),
        ]

        all_good = True
        for check_name, check_result in checks:
            if check_result:
                print(f"  ✓ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                all_good = False

        return all_good

    except Exception as e:
        print(f"  ❌ Error reading spec file: {e}")
        return False


def test_main_script():
    """Test main script exists"""
    print("Testing main script...")

    main_script = Path("storymaster/main.py")
    if not main_script.exists():
        print("  ❌ storymaster/main.py not found")
        return False

    print(f"  ✓ {main_script} exists")
    return True


def main():
    """Run all resource tests"""
    print("=" * 50)
    print("Build Resources Test")
    print("=" * 50)

    tests = [
        ("Icon Files", test_icon_files),
        ("Version Info", test_version_info),
        ("Spec File", test_spec_file),
        ("Main Script", test_main_script),
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
        print("🎉 All resource tests passed!")
        print("Build should work properly.")
        return True
    else:
        print("❌ Some resource tests failed.")
        print("Fix the issues above before building.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
