# Storymaster Linux AppImage Installation Guide

This guide covers installing Storymaster on Linux using the AppImage format.

## Quick Install

1. Make sure you have the `Storymaster-x86_64.AppImage` file in this directory
2. Run the installation script:
   ```bash
   ./install_appimage.sh
   ```
3. Launch Storymaster from your application menu or run `Storymaster-x86_64.AppImage` from the terminal

## What the Installer Does

The installation script:
- ✅ Copies the AppImage to `~/.local/bin/` (user-level, no sudo required)
- ✅ Makes the AppImage executable
- ✅ Installs application icons in multiple sizes to `~/.local/share/icons/`
- ✅ Creates a desktop launcher in `~/.local/share/applications/`
- ✅ Updates the desktop database and icon cache
- ✅ Adds Storymaster to your application menu

## Manual Installation (Alternative)

If you prefer not to use the installer, you can run the AppImage directly:

```bash
chmod +x Storymaster-x86_64.AppImage
./Storymaster-x86_64.AppImage
```

However, this won't add Storymaster to your application menu or install icons.

## Uninstalling

To remove Storymaster from your system:

```bash
./uninstall_appimage.sh
```

This removes:
- The AppImage from `~/.local/bin/`
- The desktop launcher
- All installed icons

**Note:** Your project files and databases are NOT removed during uninstallation. They remain in your home directory for future use.

## Troubleshooting

### AppImage won't run
- Make sure FUSE is installed: `sudo apt install libfuse2` (Ubuntu/Debian)
- Verify the AppImage is executable: `chmod +x Storymaster-x86_64.AppImage`

### Application doesn't appear in menu
- Log out and log back in, or restart your desktop environment
- Manually refresh the menu cache (varies by desktop environment)

### Icons don't show up
- The icon cache update may take a few minutes
- Try logging out and back in

### Permission denied errors
- The installer uses `~/.local/` which doesn't require sudo
- If you still get errors, check that `~/.local/bin` is in your `$PATH`

## Requirements

- Linux kernel 2.6.32 or later
- FUSE 2.x (for AppImage support)
- Any modern desktop environment (GNOME, KDE, XFCE, etc.)

## File Locations After Installation

- **AppImage**: `~/.local/bin/Storymaster-x86_64.AppImage`
- **Desktop Launcher**: `~/.local/share/applications/storymaster.desktop`
- **Icons**: `~/.local/share/icons/hicolor/*/apps/storymaster.{png,svg}`
- **Your Data**: Stored in your home directory (location depends on your usage)

## Development Install

For development purposes, see the main README.md or use the Python-based installer:

```bash
./scripts/install.sh
```
