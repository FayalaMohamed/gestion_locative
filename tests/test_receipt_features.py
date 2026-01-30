#!/usr/bin/env python
"""
Quick test to verify config changes for multiple signatures and company names
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.utils.config import Config

config = Config()

print("=" * 60)
print("Testing Config Changes")
print("=" * 60)

# Test company names
print("\n1. Testing Company Names:")
print("   - Getting company names:", config.get_company_names())

# Add a test name
config.add_company_name("Test Company 1")
print("   - After adding 'Test Company 1':", config.get_company_names())

config.add_company_name("Test Company 2")
print("   - After adding 'Test Company 2':", config.get_company_names())

# Test that duplicates are not added
config.add_company_name("Test Company 1")
print("   - After trying to add duplicate:", config.get_company_names())

# Test signatures
print("\n2. Testing Signatures:")
print("   - Getting signatures:", config.get_signatures())

# Add test signatures
config.add_signature("Signature A", "/path/to/sig1.png")
print("   - After adding 'Signature A':", config.get_signatures())

config.add_signature("Signature B", "/path/to/sig2.png")
print("   - After adding 'Signature B':", config.get_signatures())

# Test get_signature_path (legacy method)
print("\n3. Testing Legacy get_signature_path():")
print("   - Should return first signature path:", config.get_signature_path())

print("\n4. Testing ReceiptService import:")
try:
    from app.services.receipt_service import ReceiptService
    print("   - ReceiptService imported successfully")
except Exception as e:
    print(f"   - Error importing ReceiptService: {e}")

print("\n5. Testing ReceiptOptionsDialog import:")
try:
    from app.ui.dialogs.receipt_options_dialog import ReceiptOptionsDialog
    print("   - ReceiptOptionsDialog imported successfully")
except Exception as e:
    print(f"   - Error importing ReceiptOptionsDialog: {e}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
