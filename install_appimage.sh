#!/bin/bash
# Storymaster AppImage Installation Script for Linux
# This script installs the Storymaster AppImage to your local user directory

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPIMAGE_NAME="Storymaster-x86_64.AppImage"
APPIMAGE_PATH="$SCRIPT_DIR/$APPIMAGE_NAME"

# Installation paths (user-level, no sudo required)
INSTALL_DIR="$HOME/.local/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor"

echo "🏰 Storymaster AppImage Installer"
echo "=================================="
echo ""

# Check if AppImage exists
if [ ! -f "$APPIMAGE_PATH" ]; then
    echo "❌ Error: $APPIMAGE_NAME not found in the current directory."
    echo "   Expected location: $APPIMAGE_PATH"
    echo ""
    echo "Please make sure the AppImage is in the same directory as this script."
    exit 1
fi

echo "✓ Found $APPIMAGE_NAME"

# Create directories if they don't exist
echo "📁 Creating installation directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$APPLICATIONS_DIR"
mkdir -p "$ICONS_DIR/16x16/apps"
mkdir -p "$ICONS_DIR/32x32/apps"
mkdir -p "$ICONS_DIR/64x64/apps"
mkdir -p "$ICONS_DIR/128x128/apps"
mkdir -p "$ICONS_DIR/256x256/apps"
mkdir -p "$ICONS_DIR/512x512/apps"
mkdir -p "$ICONS_DIR/scalable/apps"

# Make AppImage executable
echo "🔧 Making AppImage executable..."
chmod +x "$APPIMAGE_PATH"

# Copy AppImage to installation directory
echo "📦 Installing AppImage to $INSTALL_DIR..."
cp "$APPIMAGE_PATH" "$INSTALL_DIR/$APPIMAGE_NAME"

# Copy icons
echo "🎨 Installing icons..."
if [ -f "$SCRIPT_DIR/assets/storymaster_icon_16.png" ]; then
    cp "$SCRIPT_DIR/assets/storymaster_icon_16.png" "$ICONS_DIR/16x16/apps/storymaster.png"
fi
if [ -f "$SCRIPT_DIR/assets/storymaster_icon_32.png" ]; then
    cp "$SCRIPT_DIR/assets/storymaster_icon_32.png" "$ICONS_DIR/32x32/apps/storymaster.png"
fi
if [ -f "$SCRIPT_DIR/assets/storymaster_icon_64.png" ]; then
    cp "$SCRIPT_DIR/assets/storymaster_icon_64.png" "$ICONS_DIR/64x64/apps/storymaster.png"
fi
if [ -f "$SCRIPT_DIR/assets/storymaster_icon_128.png" ]; then
    cp "$SCRIPT_DIR/assets/storymaster_icon_128.png" "$ICONS_DIR/128x128/apps/storymaster.png"
fi
if [ -f "$SCRIPT_DIR/assets/storymaster_icon_256.png" ]; then
    cp "$SCRIPT_DIR/assets/storymaster_icon_256.png" "$ICONS_DIR/256x256/apps/storymaster.png"
fi
if [ -f "$SCRIPT_DIR/assets/storymaster_icon_512.png" ]; then
    cp "$SCRIPT_DIR/assets/storymaster_icon_512.png" "$ICONS_DIR/512x512/apps/storymaster.png"
fi
if [ -f "$SCRIPT_DIR/assets/storymaster_icon.svg" ]; then
    cp "$SCRIPT_DIR/assets/storymaster_icon.svg" "$ICONS_DIR/scalable/apps/storymaster.svg"
fi

# Create desktop file
echo "🖥️  Creating desktop launcher..."
cat > "$APPLICATIONS_DIR/storymaster.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Storymaster
Comment=Visual Story Plotting & World-Building Tool
GenericName=Story Writing Tool
Exec=$INSTALL_DIR/$APPIMAGE_NAME %F
Icon=storymaster
Terminal=false
Categories=Office;Publishing;Education;
Keywords=writing;story;plot;worldbuilding;creative;novel;screenplay;character;arc;litographer;lorekeeper;
StartupNotify=true
MimeType=application/x-storymaster;
StartupWMClass=storymaster
Actions=NewProject;OpenProject;

[Desktop Action NewProject]
Name=New Project
Exec=$INSTALL_DIR/$APPIMAGE_NAME --new-project

[Desktop Action OpenProject]
Name=Open Project
Exec=$INSTALL_DIR/$APPIMAGE_NAME --open-project
EOF

# Make desktop file executable
chmod +x "$APPLICATIONS_DIR/storymaster.desktop"

# Update desktop database
echo "🔄 Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
fi

# Update icon cache
echo "🔄 Updating icon cache..."
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$ICONS_DIR" 2>/dev/null || true
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Storymaster has been installed to: $INSTALL_DIR/$APPIMAGE_NAME"
echo ""
echo "You can now:"
echo "  • Launch Storymaster from your application menu"
echo "  • Run it from terminal: $APPIMAGE_NAME"
echo "  • Pin it to your favorites/dock"
echo ""
echo "To uninstall, run: ./uninstall_appimage.sh"
echo ""
