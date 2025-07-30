#!/usr/bin/env python3
"""
Icon generation script for Storymaster
Creates icons in multiple formats from the base SVG
"""

import os
import subprocess
from pathlib import Path


def create_png_from_svg(svg_path, png_path, size=64):
    """Convert SVG to PNG using ImageMagick or fallback method"""
    try:
        # Try using ImageMagick convert
        subprocess.run(
            [
                "convert",
                "-background",
                "transparent",
                "-size",
                f"{size}x{size}",
                str(svg_path),
                str(png_path),
            ],
            check=True,
        )
        print(f"Created {png_path} using ImageMagick")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try using Inkscape
            subprocess.run(
                [
                    "inkscape",
                    str(svg_path),
                    "--export-png",
                    str(png_path),
                    "--export-width",
                    str(size),
                    "--export-height",
                    str(size),
                ],
                check=True,
            )
            print(f"Created {png_path} using Inkscape")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                f"Warning: Could not create {png_path} - ImageMagick or Inkscape required"
            )
            return False


def create_ico_from_png(png_path, ico_path):
    """Convert PNG to ICO using ImageMagick"""
    try:
        subprocess.run(["convert", str(png_path), str(ico_path)], check=True)
        print(f"Created {ico_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"Warning: Could not create {ico_path} - ImageMagick required")
        return False


def main():
    """Generate all icon formats"""
    base_dir = Path(__file__).parent
    assets_dir = base_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    svg_path = assets_dir / "storymaster_icon.svg"

    if not svg_path.exists():
        print(f"Error: {svg_path} not found")
        return False

    # Create PNG versions
    png_64 = assets_dir / "storymaster_icon_64.png"
    png_32 = assets_dir / "storymaster_icon_32.png"
    png_16 = assets_dir / "storymaster_icon_16.png"

    success = True
    success &= create_png_from_svg(svg_path, png_64, 64)
    success &= create_png_from_svg(svg_path, png_32, 32)
    success &= create_png_from_svg(svg_path, png_16, 16)

    # Create ICO for Windows
    if png_32.exists():
        ico_path = assets_dir / "storymaster_icon.ico"
        success &= create_ico_from_png(png_32, ico_path)

    return success


if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Icon generation completed successfully")
    else:
        print("⚠️  Some icons could not be generated (missing ImageMagick/Inkscape)")
