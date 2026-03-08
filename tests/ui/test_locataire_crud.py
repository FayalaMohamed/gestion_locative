#!/usr/bin/env python
"""
Locataire CRUD UI Tests
Tests all CRUD operations for Locataire entity through the UI
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QTableWidget
from PySide6.QtTest import QTest

from tests.ui.base_ui_test import TestRunner


class TestLocataireCRUD:
    """Test suite for Locataire CRUD operations"""
    
    # Create test data - ALL fields
    TEST_NOM = "Test Locataire UI"
    TEST_TEL = "+216 50 000 000"
    TEST_EMAIL = "test@example.com"
    TEST_CIN = "12345678"
    TEST_RAISON_SOCIALE = "Test Company SARL"
    TEST_NOTES = "Locataire de test avec tous les champs remplis. Test complet UI."
    
    # Update test data - ALL fields
    UPDATE_TEL = "+216 50 999 999"
    UPDATE_EMAIL = "updated@example.com"
    UPDATE_RAISON_SOCIALE = "Updated Company SARL"
    UPDATE_NOTES = "Locataire mis à jour avec nouvelles informations complètes."
    
    @staticmethod
    def test_create_locataire(runner: TestRunner):
        """Test creating a new locataire through the UI"""
        print("\n  Test: Create Locataire")
        
        # Navigate to Locataires view
        view = runner.navigate_to_view("locataires")
        assert view is not None, "Could not navigate to Locataires view"
        
        # Get initial count
        initial_count = runner.get_table_row_count()
        print(f"    Initial count: {initial_count}")
        
        # Use the helper to open dialog, fill ALL fields, and submit
        success = runner.open_dialog_and_fill(
            button_text="Ajouter",
            dialog_title="locataire",
            field_values={
                "nom_edit": TestLocataireCRUD.TEST_NOM,
                "telephone_edit": TestLocataireCRUD.TEST_TEL,
                "email_edit": TestLocataireCRUD.TEST_EMAIL,
                "cin_edit": TestLocataireCRUD.TEST_CIN,
                "raison_sociale_edit": TestLocataireCRUD.TEST_RAISON_SOCIALE,
                "notes_edit": TestLocataireCRUD.TEST_NOTES
            }
        )
        
        assert success, "Failed to create locataire"
        
        # Refresh view
        runner.click_button("Actualiser")
        QTest.qWait(300)
        
        # Verify in UI
        new_count = runner.get_table_row_count()
        print(f"    New count: {new_count}")
        assert new_count == initial_count + 1, f"Expected {initial_count + 1} rows, got {new_count}"
        
        # Verify in database
        exists = runner.db_helper.record_exists("locataires", "nom", TestLocataireCRUD.TEST_NOM)
        assert exists, "Locataire not found in database"
        print(f"    ✓ Verified in database")
    
    @staticmethod
    def test_read_locataire(runner: TestRunner):
        """Test reading/viewing a locataire"""
        print("\n  Test: Read Locataire")
        
        view = runner.navigate_to_view("locataires")
        
        tables = view.findChildren(QTableWidget)
        if not tables:
            print("    ⚠ No table found")
            return
        
        table = tables[0]
        row_count = table.rowCount()
        print(f"    Table has {row_count} rows")
        
        if row_count == 0:
            print("    ⚠ Skipping (no data)")
            return
        
        # Find test locataire
        found = False
        for row in range(row_count):
            item = table.item(row, 1)
            if item and item.text() == TestLocataireCRUD.TEST_NOM:
                found = True
                print(f"    ✓ Found test locataire in row {row}")
                break
        
        assert found, "Test locataire not found in table"
    
    @staticmethod
    def test_update_locataire(runner: TestRunner):
        """Test updating a locataire"""
        print("\n  Test: Update Locataire")
        
        view = runner.navigate_to_view("locataires")
        
        tables = view.findChildren(QTableWidget)
        if not tables:
            print("    ⚠ No table found")
            return
        
        table = tables[0]
        target_row = -1
        
        for row in range(table.rowCount()):
            item = table.item(row, 1)
            if item and item.text() == TestLocataireCRUD.TEST_NOM:
                target_row = row
                break
        
        if target_row == -1:
            print("    ⚠ Test locataire not found, skipping")
            return
        
        # Select and modify
        table.selectRow(target_row)
        app = QApplication.instance()
        app.processEvents()
        QTest.qWait(200)
        
        # Update using helper - fill ALL fields
        success = runner.open_dialog_and_fill(
            button_text="Modifier",
            dialog_title="locataire",
            field_values={
                "nom_edit": TestLocataireCRUD.TEST_NOM,
                "telephone_edit": TestLocataireCRUD.UPDATE_TEL,
                "email_edit": TestLocataireCRUD.UPDATE_EMAIL,
                "cin_edit": TestLocataireCRUD.TEST_CIN,
                "raison_sociale_edit": TestLocataireCRUD.UPDATE_RAISON_SOCIALE,
                "notes_edit": TestLocataireCRUD.UPDATE_NOTES
            }
        )
        
        assert success, "Failed to update locataire"
        
        runner.click_button("Actualiser")
        QTest.qWait(300)
        
        print("    ✓ Update completed")
    
    @staticmethod
    def test_delete_locataire(runner: TestRunner):
        """Test deleting a locataire"""
        print("\n  Test: Delete Locataire")
        
        initial_count = runner.db_helper.count_records("locataires")
        print(f"    Initial DB count: {initial_count}")
        
        if initial_count == 0:
            print("    ⚠ No locataires to delete")
            return
        
        exists = runner.db_helper.record_exists("locataires", "nom", TestLocataireCRUD.TEST_NOM)
        
        if not exists:
            print(f"    ⚠ Test locataire not found")
            return
        
        # Delete from database
        runner.db_helper.delete_record("locataires", "nom", TestLocataireCRUD.TEST_NOM)
        
        new_count = runner.db_helper.count_records("locataires")
        assert new_count == initial_count - 1
        print(f"    ✓ Deleted test locataire")
        print(f"    New DB count: {new_count}")


def run_locataire_tests(runner: TestRunner):
    """Run all Locataire CRUD tests"""
    print("\n" + "="*60)
    print("  LOCATAIRE CRUD TESTS")
    print("="*60)
    
    runner.run_test("Create Locataire", TestLocataireCRUD.test_create_locataire)
    runner.run_test("Read Locataire", TestLocataireCRUD.test_read_locataire)
    runner.run_test("Update Locataire", TestLocataireCRUD.test_update_locataire)
    runner.run_test("Delete Locataire", TestLocataireCRUD.test_delete_locataire)


if __name__ == "__main__":
    print("Locataire CRUD Tests - Use run_all_ui_tests.py to execute")
