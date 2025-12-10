#!/bin/bash
# Storymaster AppImage Uninstallation Script for Linux
# This script removes Storymaster AppImage from your local user directory

APPIMAGE_NAME="Storymaster-x86_64.AppImage"
INSTALL_DIR="$HOME/.local/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor"

echo "🏰 Storymaster AppImage Uninstaller"
echo "===================================="
echo ""
echo "This will remove Storymaster from your system."
echo ""
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo ""
echo "🗑️  Removing Storymaster..."

# Remove AppImage
if [ -f "$INSTALL_DIR/$APPIMAGE_NAME" ]; then
    echo "  Removing AppImage..."
    rm "$INSTALL_DIR/$APPIMAGE_NAME"
fi

# Remove desktop file
if [ -f "$APPLICATIONS_DIR/storymaster.desktop" ]; then
    echo "  Removing desktop launcher..."
    rm "$APPLICATIONS_DIR/storymaster.desktop"
fi

# Remove icons
echo "  Removing icons..."
rm -f "$ICONS_DIR/16x16/apps/storymaster.png"
rm -f "$ICONS_DIR/32x32/apps/storymaster.png"
rm -f "$ICONS_DIR/64x64/apps/storymaster.png"
rm -f "$ICONS_DIR/128x128/apps/storymaster.png"
rm -f "$ICONS_DIR/256x256/apps/storymaster.png"
rm -f "$ICONS_DIR/512x512/apps/storymaster.png"
rm -f "$ICONS_DIR/scalable/apps/storymaster.svg"

# Update desktop database
echo "  Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
fi

# Update icon cache
echo "  Updating icon cache..."
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$ICONS_DIR" 2>/dev/null || true
fi

echo ""
echo "✅ Storymaster has been uninstalled."
echo ""
echo "Note: Your projects and database files have NOT been removed."
echo "They are located in your home directory and can be manually deleted if needed."
echo ""
