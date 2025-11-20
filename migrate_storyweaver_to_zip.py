#!/usr/bin/env python3
"""
Migration utility to convert old .storyweaver directory bundles to new ZIP format.

Usage:
    python migrate_storyweaver_to_zip.py <path_to_directory>
    python migrate_storyweaver_to_zip.py --scan <directory_to_scan>

Examples:
    # Convert a single document
    python migrate_storyweaver_to_zip.py ./my_story.storyweaver

    # Scan and convert all documents in a directory
    python migrate_storyweaver_to_zip.py --scan ~/Documents
"""
import argparse
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from datetime import datetime


def is_old_format_directory(path: str) -> bool:
    """Check if path is an old-format .storyweaver directory."""
    if not os.path.isdir(path):
        return False
    if not path.endswith('.storyweaver'):
        return False

    # Check for document.md or metadata.json
    doc_file = os.path.join(path, 'document.md')
    meta_file = os.path.join(path, 'metadata.json')

    return os.path.isfile(doc_file) or os.path.isfile(meta_file)


def convert_directory_to_zip(dir_path: str, backup: bool = True, remove_old: bool = False) -> bool:
    """
    Convert an old-format .storyweaver directory to new ZIP format.

    Args:
        dir_path: Path to the .storyweaver directory
        backup: Create a backup before conversion
        remove_old: Remove old directory after successful conversion

    Returns:
        True if conversion successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Converting: {dir_path}")
    print(f"{'='*60}")

    try:
        # Validate input
        if not is_old_format_directory(dir_path):
            print(f"❌ ERROR: Not a valid old-format .storyweaver directory")
            return False

        # Create backup if requested
        if backup:
            backup_path = f"{dir_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"📦 Creating backup: {backup_path}")
            shutil.copytree(dir_path, backup_path)
            print(f"   ✓ Backup created")

        # Read old format files
        doc_file = os.path.join(dir_path, 'document.md')
        meta_file = os.path.join(dir_path, 'metadata.json')

        print(f"\n📄 Reading old format files...")

        # Read document.md
        if os.path.isfile(doc_file):
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   ✓ document.md: {len(content)} characters")
        else:
            content = ""
            print(f"   ⚠ document.md not found, using empty content")

        # Read metadata.json
        if os.path.isfile(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"   ✓ metadata.json: {len(metadata.get('entity_map', {}))} entities")
        else:
            metadata = {
                "storymaster_db": "",
                "last_sync": datetime.now().isoformat(),
                "entity_map": {}
            }
            print(f"   ⚠ metadata.json not found, using defaults")

        # Create new ZIP file (temporary name first)
        zip_path = f"{dir_path}.zip.tmp"
        print(f"\n💾 Creating ZIP file: {os.path.basename(dir_path)}")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Write document.md
            zf.writestr('document.md', content.encode('utf-8'))
            print(f"   ✓ Added document.md")

            # Update last sync time
            metadata["last_sync"] = datetime.now().isoformat()

            # Write metadata.json
            metadata_json = json.dumps(metadata, indent=2)
            zf.writestr('metadata.json', metadata_json.encode('utf-8'))
            print(f"   ✓ Added metadata.json")

        # Get file size info
        zip_size = os.path.getsize(zip_path)
        print(f"   ✓ ZIP file created: {zip_size:,} bytes")

        # Rename to final name
        final_path = dir_path  # Keep same name (will be a file now)

        # Remove old directory if requested or rename it
        if remove_old:
            print(f"\n🗑️  Removing old directory...")
            shutil.rmtree(dir_path)
            print(f"   ✓ Old directory removed")
        else:
            # Rename old directory to .old
            old_renamed = f"{dir_path}.old"
            if os.path.exists(old_renamed):
                shutil.rmtree(old_renamed)
            shutil.move(dir_path, old_renamed)
            print(f"\n📁 Renamed old directory to: {os.path.basename(old_renamed)}")

        # Move ZIP to final location
        shutil.move(zip_path, final_path)
        print(f"✅ Conversion complete: {os.path.basename(final_path)}")

        return True

    except Exception as e:
        import traceback
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()

        # Clean up temp file if exists
        zip_path = f"{dir_path}.zip.tmp"
        if os.path.exists(zip_path):
            os.unlink(zip_path)

        return False


def find_old_format_documents(root_dir: str) -> list:
    """
    Recursively find all old-format .storyweaver directories.

    Args:
        root_dir: Root directory to search

    Returns:
        List of paths to old-format .storyweaver directories
    """
    old_docs = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            if is_old_format_directory(full_path):
                old_docs.append(full_path)

    return old_docs


def main():
    parser = argparse.ArgumentParser(
        description="Convert old .storyweaver directory bundles to new ZIP format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single document
  %(prog)s ./my_story.storyweaver

  # Scan and convert all documents in a directory
  %(prog)s --scan ~/Documents

  # Convert without backup
  %(prog)s --no-backup ./my_story.storyweaver

  # Convert and remove old directory
  %(prog)s --remove-old ./my_story.storyweaver
        """
    )

    parser.add_argument(
        'path',
        nargs='?',
        help='Path to .storyweaver directory to convert'
    )

    parser.add_argument(
        '--scan',
        metavar='DIR',
        help='Scan directory recursively and convert all old-format documents'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup before conversion'
    )

    parser.add_argument(
        '--remove-old',
        action='store_true',
        help='Remove old directory after successful conversion (default: rename to .old)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be converted without actually converting'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.path and not args.scan:
        parser.print_help()
        sys.exit(1)

    print("\n" + "="*60)
    print("Storyweaver Format Migration Utility")
    print("Directory → ZIP Conversion")
    print("="*60)

    if args.scan:
        # Scan mode
        scan_dir = os.path.expanduser(args.scan)
        print(f"\n🔍 Scanning: {scan_dir}")

        if not os.path.isdir(scan_dir):
            print(f"❌ ERROR: Directory not found: {scan_dir}")
            sys.exit(1)

        old_docs = find_old_format_documents(scan_dir)

        if not old_docs:
            print(f"\n✓ No old-format .storyweaver directories found")
            sys.exit(0)

        print(f"\n📋 Found {len(old_docs)} old-format document(s):")
        for doc in old_docs:
            print(f"   • {doc}")

        if args.dry_run:
            print(f"\n[DRY RUN] Would convert {len(old_docs)} document(s)")
            sys.exit(0)

        # Ask for confirmation
        response = input(f"\nConvert {len(old_docs)} document(s)? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            sys.exit(0)

        # Convert all
        results = []
        for doc in old_docs:
            success = convert_directory_to_zip(
                doc,
                backup=not args.no_backup,
                remove_old=args.remove_old
            )
            results.append((doc, success))

        # Summary
        print(f"\n{'='*60}")
        print("CONVERSION SUMMARY")
        print(f"{'='*60}")

        successful = sum(1 for _, s in results if s)
        failed = len(results) - successful

        for doc, success in results:
            status = "✅" if success else "❌"
            print(f"{status} {os.path.basename(doc)}")

        print(f"\nTotal: {successful}/{len(results)} converted successfully")

        if failed > 0:
            sys.exit(1)

    else:
        # Single document mode
        doc_path = os.path.expanduser(args.path)

        if not os.path.exists(doc_path):
            print(f"❌ ERROR: Path not found: {doc_path}")
            sys.exit(1)

        if args.dry_run:
            if is_old_format_directory(doc_path):
                print(f"[DRY RUN] Would convert: {doc_path}")
            else:
                print(f"[DRY RUN] Not an old-format directory: {doc_path}")
            sys.exit(0)

        success = convert_directory_to_zip(
            doc_path,
            backup=not args.no_backup,
            remove_old=args.remove_old
        )

        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
