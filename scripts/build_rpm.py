#!/usr/bin/env python3
"""
RPM Package Builder for Storymaster

This script creates an RPM package for Linux distributions.
Requires rpmbuild and standard RPM build tools.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def print_header():
    """Print build header"""
    print("=" * 60)
    print("[PACKAGE] Storymaster RPM Builder")
    print("   Linux RPM package creation")
    print("=" * 60)
    print()


def check_rpm_build_tools():
    """Check if RPM build tools are available"""
    print("[CHECK] Checking RPM build tools...")

    required_tools = ["rpmbuild", "tar", "gzip"]

    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            print(f"[OK] {tool} found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"[ERROR] {tool} not found")
            print(f"   Install with: sudo dnf install rpm-build (Fedora/RHEL)")
            print(f"   or: sudo apt install rpm (Debian/Ubuntu)")
            return False

    return True


def create_source_tarball():
    """Create source tarball for RPM build"""
    print("\n[FILES] Creating source tarball...")

    try:
        # Create temporary directory for source
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "storymaster-1.0.0"
            source_dir.mkdir()

            # Copy source files
            # Copy files that exist
            base_files = [
                "storymaster/",
                "tests/",
                "scripts/",  # Include scripts directory
                "requirements.txt",
                "assets/",  # Include assets directory with icons
            ]

            # Optional files
            optional_files = ["README.md", "CLAUDE.md"]

            files_to_copy = base_files + [f for f in optional_files if Path(f).exists()]

            for file_path in files_to_copy:
                src = Path(file_path)
                if src.exists():
                    if src.is_dir():
                        shutil.copytree(src, source_dir / src.name)
                    else:
                        shutil.copy2(src, source_dir / src.name)
                    print(f"   Copied {file_path}")

            # Create tarball
            tarball_name = "storymaster-1.0.0.tar.gz"

            # Change to temp directory for tar creation
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            subprocess.run(
                ["tar", "czf", original_dir + "/" + tarball_name, "storymaster-1.0.0"],
                check=True,
            )

            os.chdir(original_dir)

        print(f"[OK] Source tarball created: {tarball_name}")
        return tarball_name

    except Exception as e:
        print(f"[ERROR] Failed to create source tarball: {e}")
        return None


def setup_rpm_build_tree():
    """Set up RPM build directory structure"""
    print("\n[BUILD]  Setting up RPM build tree...")

    home_dir = Path.home()
    rpmbuild_dir = home_dir / "rpmbuild"

    # Create RPM build directories
    for subdir in ["BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
        (rpmbuild_dir / subdir).mkdir(parents=True, exist_ok=True)

    print(f"[OK] RPM build tree created at {rpmbuild_dir}")
    return rpmbuild_dir


def build_rpm_package(tarball_name, rpmbuild_dir):
    """Build the RPM package"""
    print("\n[COMPILE] Building RPM package...")

    try:
        # Copy source tarball to SOURCES
        shutil.copy2(tarball_name, rpmbuild_dir / "SOURCES" / tarball_name)

        # Copy spec file to SPECS
        shutil.copy2(
            "storymaster.spec.rpm", rpmbuild_dir / "SPECS" / "storymaster.spec"
        )

        # Build the RPM
        cmd = [
            "rpmbuild",
            "-ba",  # Build both binary and source RPM
            str(rpmbuild_dir / "SPECS" / "storymaster.spec"),
        ]

        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("[OK] RPM package built successfully!")

        # Find and report the created RPM files
        rpms_dir = rpmbuild_dir / "RPMS" / "noarch"
        srpms_dir = rpmbuild_dir / "SRPMS"

        print("\n[PACKAGE] Created packages:")
        for rpm_file in rpms_dir.glob("storymaster*.rpm"):
            print(f"   • Binary RPM: {rpm_file}")

        for srpm_file in srpms_dir.glob("storymaster*.rpm"):
            print(f"   • Source RPM: {srpm_file}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] RPM build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def create_installation_instructions():
    """Create installation instructions for the RPM"""
    print("\n[NOTE] Creating installation instructions...")

    instructions = """# Storymaster RPM Installation

## Installing the RPM

### Fedora/RHEL/CentOS:
```bash
sudo dnf install ./storymaster-1.0.0-1.*.noarch.rpm
```

### OpenSUSE:
```bash
sudo zypper install ./storymaster-1.0.0-1.*.noarch.rpm
```

### Generic RPM:
```bash
sudo rpm -i storymaster-1.0.0-1.*.noarch.rpm
```

## Dependencies

The RPM will automatically install required Python dependencies:
- python3 >= 3.8
- python3-PySide6
- python3-sqlalchemy >= 2.0

## Running Storymaster

After installation:
```bash
storymaster
```

Or find it in your applications menu under "Office" or "Publishing".

## First Run

On first run, Storymaster will:
1. Create a database in `~/.local/share/storymaster/`
2. Ask if you want to load sample data
3. Launch the application

## Uninstalling

```bash
sudo rpm -e storymaster
```

## User Data Location

Your stories are stored in:
`~/.local/share/storymaster/storymaster.db`

To backup, simply copy this file.
"""

    with open("RPM_INSTALL.md", "w") as f:
        f.write(instructions)

    print("[OK] Installation instructions created: RPM_INSTALL.md")


def print_completion_info():
    """Print build completion information"""
    home_dir = Path.home()
    rpmbuild_dir = home_dir / "rpmbuild"

    print("\n" + "=" * 60)
    print("[SUCCESS] RPM Build Complete!")
    print("=" * 60)
    print()
    print("[FILES] Package locations:")
    print(f"   • Binary RPMs: {rpmbuild_dir}/RPMS/noarch/")
    print(f"   • Source RPMs: {rpmbuild_dir}/SRPMS/")
    print()
    print("[DEPLOY] To distribute:")
    print("   1. Share the .noarch.rpm file")
    print("   2. Users install with: sudo dnf/zypper/rpm install <file>")
    print("   3. Application appears in system menus")
    print()
    print("[CHECK] Installation:")
    print("   • System-wide installation in /usr/share/storymaster/")
    print("   • Launcher script in /usr/bin/storymaster")
    print("   • Desktop entry for GUI integration")
    print("   • User data in ~/.local/share/storymaster/")
    print("=" * 60)


def main():
    """Main build process"""
    print_header()

    # Check if we're on a system that can build RPMs
    if (
        not Path("/etc/redhat-release").exists()
        and not Path("/etc/fedora-release").exists()
    ):
        print("[WARNING]  This doesn't appear to be a Red Hat-based system.")
        print("   RPM building is optimized for Fedora/RHEL/CentOS.")
        print("   You can still try, but may encounter issues.")
        print()

    # Build steps
    if not check_rpm_build_tools():
        return False

    tarball = create_source_tarball()
    if not tarball:
        return False

    rpmbuild_dir = setup_rpm_build_tree()

    if not build_rpm_package(tarball, rpmbuild_dir):
        return False

    create_installation_instructions()
    print_completion_info()

    # Cleanup
    Path(tarball).unlink()
    print(f"\n[CLEAN] Cleaned up temporary files")

    return True


if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[WARNING]  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during build: {e}")
        sys.exit(1)
