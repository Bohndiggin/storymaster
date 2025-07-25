#!/usr/bin/env python3
"""
Storymaster Installation Script

This script sets up Storymaster for first-time users by:
1. Checking Python version compatibility
2. Creating a virtual environment
3. Installing dependencies
4. Initializing the SQLite database
5. Seeding with sample data (optional)

Run: python install.py
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def print_header():
    """Print installation header"""
    print("=" * 60)
    print("🏰 Storymaster Installation Script")
    print("   Visual Story Plotting & World-Building Tool")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    version = sys.version_info

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported.")
        print("   Storymaster requires Python 3.8 or higher.")
        print("   Please upgrade Python and try again.")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible!")
    return True


def check_dependencies():
    """Check if required system dependencies are available"""
    print("\n📋 Checking system dependencies...")

    # Check if we can create virtual environments
    try:
        import venv

        print("✅ venv module available")
    except ImportError:
        print("❌ venv module not available. Please install python3-venv")
        return False

    return True


def create_virtual_environment():
    """Create and activate virtual environment"""
    print("\n🏗️  Creating virtual environment...")

    venv_path = Path(".venv")

    if venv_path.exists():
        print("⚠️  Virtual environment already exists. Skipping creation.")
        return True

    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created at .venv/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_activation_command():
    """Get the command to activate virtual environment based on OS"""
    if platform.system() == "Windows":
        return ".venv\\Scripts\\activate"
    else:
        return "source .venv/bin/activate"


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")

    # Determine pip path based on OS
    if platform.system() == "Windows":
        pip_path = ".venv\\Scripts\\pip"
    else:
        pip_path = ".venv/bin/pip"

    try:
        # Upgrade pip first
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)

        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print(
            "❌ requirements.txt not found. Please ensure you're in the Storymaster directory."
        )
        return False


def setup_environment():
    """Setup environment configuration"""
    print("\n⚙️  Setting up environment configuration...")

    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists. Skipping environment setup.")
        return True

    # Create .env file with SQLite configuration
    env_content = """DATABASE_CONNECTION="sqlite:///storymaster.db"
TEST_DATABASE_CONNECTION="sqlite:///test_storymaster.db"
"""

    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Environment configuration created!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def initialize_database():
    """Initialize SQLite database"""
    print("\n🗄️  Initializing database...")

    # Check if database already exists
    if Path("storymaster.db").exists():
        print("⚠️  Database already exists. Skipping initialization.")
        return True

    # Determine python path based on OS
    if platform.system() == "Windows":
        python_path = ".venv\\Scripts\\python"
    else:
        python_path = ".venv/bin/python"

    try:
        subprocess.run([python_path, "init_database.py"], check=True)
        print("✅ Database initialized successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize database: {e}")
        return False


def seed_database():
    """Seed database with sample data"""
    print("\n🌱 Do you want to seed the database with sample data?")
    print("   This includes example characters, locations, and story nodes.")

    while True:
        choice = input("   Seed database? (y/n): ").lower().strip()
        if choice in ["y", "yes"]:
            break
        elif choice in ["n", "no"]:
            print("⚠️  Skipping database seeding. You'll start with an empty database.")
            return True
        else:
            print("   Please enter 'y' for yes or 'n' for no.")

    print("\n🌱 Seeding database with sample data...")

    # Determine python path based on OS
    if platform.system() == "Windows":
        python_path = ".venv\\Scripts\\python"
    else:
        python_path = ".venv/bin/python"

    try:
        subprocess.run([python_path, "seed.py"], check=True)
        print("✅ Database seeded with sample data!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to seed database: {e}")
        print("   You can seed the database later by running: python seed.py")
        return False


def print_completion_message():
    """Print installation completion message"""
    activation_cmd = get_activation_command()

    print("\n" + "=" * 60)
    print("🎉 Installation Complete!")
    print("=" * 60)
    print()
    print("To start using Storymaster:")
    print(f"1. Activate the virtual environment: {activation_cmd}")
    print("2. Run the application: python storymaster/main.py")
    print()
    print("📚 Features:")
    print("   • Litographer: Visual node-based story plotting")
    print("   • Lorekeeper: Database-driven world building")
    print("   • Plot Management: Create and switch between multiple plots")
    print()
    print("🆘 Need help? Check the documentation or create an issue on GitHub")
    print("=" * 60)


def main():
    """Main installation process"""
    print_header()

    # Pre-flight checks
    if not check_python_version():
        sys.exit(1)

    if not check_dependencies():
        sys.exit(1)

    # Installation steps
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Initializing database", initialize_database),
        ("Seeding database", seed_database),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Installation failed at: {step_name}")
            print("Please resolve the error and run the installer again.")
            sys.exit(1)

    print_completion_message()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during installation: {e}")
        sys.exit(1)
