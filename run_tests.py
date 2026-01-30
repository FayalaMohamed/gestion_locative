#!/usr/bin/env python
"""
Test runner script for Gestion Locative Pro
Runs all test files and reports results
"""
import sys
import os
import subprocess
from pathlib import Path

# Test files to run (in order)
TEST_FILES = [
    ('test_crud.py', 'CRUD Operations'),
    ('test_backup.py', 'Backup Functionality'),
    ('test_relation.py', 'Relationship Tests'),
    ('test_update_system.py', 'Update System'),
]

# Non-test utilities (not run as tests)
SKIP_FILES = ['__init__.py', 'query_db.py']


def get_test_files():
    """Get list of test files from tests directory"""
    tests_dir = Path(__file__).resolve().parent
    test_files = []

    for filename in sorted(tests_dir.iterdir()):
        if filename.is_file() and filename.name.endswith('.py'):
            if filename.name in SKIP_FILES:
                continue
            if filename.name.startswith('test_'):
                test_files.append(filename)

    return test_files


def run_test_file(filepath, description):
    """Run a single test file and capture results"""
    print("\n" + "=" * 70)
    print(f"  {description}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, str(filepath)],
        capture_output=True,
        text=True,
        cwd=filepath.parent.parent
    )

    return {
        'filename': filepath.name,
        'filepath': filepath,
        'description': description,
        'return_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'success': result.returncode == 0
    }


def main():
    """Run all tests and report results"""
    print("=" * 70)
    print("  GESTION LOCATIVE PRO - TEST RUNNER")
    print("=" * 70)
    print(f"\nPython: {sys.executable}")
    print(f"Date:    2026-01-22")

    results = []
    passed = 0
    failed = 0

    for filename, description in TEST_FILES:
        filepath = Path(__file__).resolve().parent / 'tests' / filename

        if not filepath.exists():
            print(f"\n[SKIP] {filename} - File not found")
            results.append({
                'filename': filename,
                'description': description,
                'success': None,
                'reason': 'File not found'
            })
            continue

        result = run_test_file(filepath, description)
        results.append(result)

        if result['success']:
            passed += 1
            print(f"\n[PASS] {filename}")
        else:
            failed += 1
            print(f"\n[FAIL] {filename}")

            # Show last 20 lines of output for failed tests
            lines = result['stdout'].split('\n')
            if lines:
                print("\n--- Output (last 20 lines) ---")
                for line in lines[-20:]:
                    print(line)

            if result['stderr']:
                print("\n--- Errors ---")
                print(result['stderr'][-500:] if len(result['stderr']) > 500 else result['stderr'])

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    total = passed + failed
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")

    if failed > 0:
        print("\nFailed tests:")
        for r in results:
            if not r['success']:
                print(f"  - {r['filename']}")

    print("\n" + "=" * 70)

    if failed > 0:
        print("  STATUS: SOME TESTS FAILED")
    else:
        print("  STATUS: ALL TESTS PASSED")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
