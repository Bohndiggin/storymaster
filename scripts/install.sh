#!/bin/bash
# Storymaster Installation Script for Linux/Mac

echo "🏰 Installing Storymaster..."
echo "=============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Run the Python installer
python3 install.py

# Make the database files writable
chmod 664 *.db 2>/dev/null || true

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To run Storymaster:"
echo "  source .venv/bin/activate"
echo "  python storymaster/main.py"