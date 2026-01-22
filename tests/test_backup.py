#!/usr/bin/env python
"""
Test script for Google Drive backup functionality
This script demonstrates how to backup and restore the database
"""
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.services.backup_service import BackupService
from app.services.data_service import DataService


_created_backup_files = []


def cleanup_backups():
    """Clean up backup files created during tests"""
    global _created_backup_files
    for file_path in _created_backup_files:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"  Cleaned up: {file_path}")
        except Exception as e:
            print(f"  Failed to clean up {file_path}: {e}")
    _created_backup_files.clear()


def test_local_backup():
    """Test local backup functionality"""
    print("Testing local backup...")
    backup_service = BackupService()

    result = backup_service.backup_to_local()

    if result['success']:
        print(f"[OK] Local backup successful!")
        print(f"  File: {result['file_path']}")
        print(f"  Size: {result['file_size']} bytes")
        print(f"  Date: {result['backup_date']}")
        _created_backup_files.append(result['file_path'])
    else:
        print(f"[FAIL] Local backup failed: {result.get('error')}")

    return result['success']


def test_data_export():
    """Test data export functionality"""
    print("\nTesting data export...")
    try:
        data_service = DataService()
        data = data_service.export_all()

        print(f"[OK] Data export successful!")
        print(f"  Entities: {', '.join(data['entities'].keys())}")
        print(f"  Export date: {data['export_date']}")
        print(f"  Version: {data['version']}")

        return True
    except Exception as e:
        print(f"[FAIL] Data export failed: {e}")
        return False


def test_google_drive_connection():
    """Test Google Drive connection (will fail without credentials)"""
    print("\nTesting Google Drive connection...")
    backup_service = BackupService()

    if backup_service.is_authenticated():
        print("[OK] Already authenticated with Google Drive")
        return True
    else:
        print("[INFO] Not authenticated with Google Drive")
        print("  To authenticate, you need to:")
        print("  1. Set up Google Drive API credentials (see docs/GOOGLE_DRIVE_SETUP.md)")
        print("  2. Run the application and go to Settings")
        print("  3. Click 'Se connecter a Google Drive...'")
        return None  # Not authenticated, but not an error


def main():
    global _created_backup_files

    print("=" * 60)
    print("Gestion Locative Pro - Backup Feature Test")
    print("=" * 60)

    try:
        results = {
            'local_backup': test_local_backup(),
            'data_export': test_data_export(),
            'google_drive': test_google_drive_connection()
        }

        print("\n" + "=" * 60)
        print("Test Results:")
        print("=" * 60)

        for test_name, result in results.items():
            status = "[PASS]" if result is True else ("[SKIP]" if result is None else "[FAIL]")
            print(f"  {test_name}: {status}")

        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. To use Google Drive backup:")
        print("   - Read docs/GOOGLE_DRIVE_SETUP.md")
        print("   - Create Google Cloud credentials")
        print("   - Run the app and go to Settings")
        print("   - Click 'Se connecter a Google Drive...'")
        print("")
        print("2. To restore from backup:")
        print("   - Go to Settings in the app")
        print("   - Click 'Importer depuis JSON...'")
        print("   - Select a backup file")
        print("")

        return all(result is True or result is None for result in results.values())
    finally:
        if _created_backup_files:
            print("\n" + "=" * 60)
            print("Cleaning up test backup files...")
            print("=" * 60)
            cleanup_backups()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
