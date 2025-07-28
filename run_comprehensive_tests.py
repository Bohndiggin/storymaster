#!/usr/bin/env python3
"""
Comprehensive test runner for Storymaster
Runs all tests with proper configuration and reporting
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_pattern=None, verbose=False, coverage=False, quick=False):
    """
    Run the test suite with various options

    Args:
        test_pattern: Pattern to match test files (e.g., "spell_check")
        verbose: Run tests in verbose mode
        coverage: Generate coverage report
        quick: Run only fast tests (skip integration tests)
    """

    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add test directory
    cmd.append("tests/")

    # Add options based on parameters
    if verbose:
        cmd.extend(["-v", "-s"])
    else:
        cmd.append("-q")

    # Test pattern filtering
    if test_pattern:
        cmd.extend(["-k", test_pattern])

    # Quick mode - skip slow integration tests
    if quick:
        cmd.extend(["-m", "not integration"])

    # Coverage reporting
    if coverage:
        cmd.extend(
            ["--cov=storymaster", "--cov-report=html", "--cov-report=term-missing"]
        )

    # Additional useful options
    cmd.extend(
        [
            "--tb=short",  # Shorter traceback format
            "--disable-warnings",  # Reduce noise from dependencies
        ]
    )

    print("Running Storymaster Test Suite")
    print("=" * 50)
    print(f"Command: {' '.join(cmd)}")
    print()

    # Run the tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def run_specific_test_suites():
    """Run specific test suites individually"""

    test_suites = [
        ("Spell Check System", "test_spell_check_system.py"),
        ("Tab Navigation", "test_tab_navigation_system.py"),
        ("Database Models", "test_enhanced_database_models.py"),
        ("UI Components", "test_enhanced_ui_components.py"),
        ("Integration Tests", "test_comprehensive_integration.py"),
    ]

    print("Running Individual Test Suites")
    print("=" * 50)

    results = []

    for suite_name, test_file in test_suites:
        print(f"\nRunning {suite_name}...")
        print("-" * 30)

        cmd = [sys.executable, "-m", "pytest", f"tests/{test_file}", "-v", "--tb=short"]

        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode == 0:
                print(f"✓ {suite_name} - PASSED")
                results.append((suite_name, "PASSED"))
            else:
                print(f"✗ {suite_name} - FAILED")
                results.append((suite_name, "FAILED"))

        except Exception as e:
            print(f"! {suite_name} - ERROR: {e}")
            results.append((suite_name, "ERROR"))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUITE SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)

    for suite_name, status in results:
        status_icon = "✓" if status == "PASSED" else "✗" if status == "FAILED" else "!"
        print(f"{status_icon} {suite_name:<25} {status}")

    print(f"\nOverall: {passed}/{total} test suites passed")

    return 0 if passed == total else 1


def check_test_dependencies():
    """Check if all test dependencies are available"""

    print("Checking Test Dependencies...")
    print("-" * 30)

    dependencies = [
        ("pytest", "pytest"),
        ("PyQt6", "PyQt6.QtWidgets"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Mock", "unittest.mock"),
    ]

    missing_deps = []

    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✓ {dep_name}")
        except ImportError:
            print(f"✗ {dep_name} - MISSING")
            missing_deps.append(dep_name)

    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install -r requirements.txt")
        return False

    print("\nAll test dependencies available")
    return True


def main():
    """Main test runner function"""

    parser = argparse.ArgumentParser(description="Storymaster Test Runner")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Run tests in verbose mode"
    )
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument(
        "-q",
        "--quick",
        action="store_true",
        help="Run only fast tests (skip integration)",
    )
    parser.add_argument("-k", "--pattern", type=str, help="Run tests matching pattern")
    parser.add_argument(
        "--suites", action="store_true", help="Run test suites individually"
    )
    parser.add_argument(
        "--check-deps", action="store_true", help="Check test dependencies"
    )

    args = parser.parse_args()

    # Check dependencies if requested
    if args.check_deps:
        if not check_test_dependencies():
            return 1
        return 0

    # Check basic dependencies
    if not check_test_dependencies():
        print("\nCannot run tests due to missing dependencies")
        return 1

    print()

    # Run individual test suites
    if args.suites:
        return run_specific_test_suites()

    # Run all tests with options
    return run_tests(
        test_pattern=args.pattern,
        verbose=args.verbose,
        coverage=args.coverage,
        quick=args.quick,
    )


if __name__ == "__main__":
    sys.exit(main())
