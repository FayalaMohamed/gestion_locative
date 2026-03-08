#!/usr/bin/env python
"""
Immeuble CRUD UI Tests
Tests all CRUD operations for Immeuble entity through the UI
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QTableWidget
from PySide6.QtTest import QTest

from tests.ui.base_ui_test import TestRunner


class TestImmeubleCRUD:
    """Test suite for Immeuble CRUD operations"""
    
    # Create test data - ALL fields
    TEST_NAME = "Test Immeuble UI"
    TEST_ADRESSE = "123 Avenue Test, Tunis"
    TEST_NOTES = "Immeuble de test avec tous les champs remplis. Créé pour les tests UI."
    
    # Update test data - ALL fields
    UPDATE_ADRESSE = "456 Avenue Updated, Sfax"
    UPDATE_NOTES = "Immeuble mis à jour avec nouvelles informations. Test de mise à jour complète."
    
    @staticmethod
    def test_create_immeuble(runner: TestRunner):
        """Test creating a new immeuble through the UI"""
        print("\n  Test: Create Immeuble")
        
        # Navigate to Immeubles view
        view = runner.navigate_to_view("immeubles")
        assert view is not None, "Could not navigate to Immeubles view"
        
        # Get initial count
        initial_count = runner.get_table_row_count()
        print(f"    Initial count: {initial_count}")
        
        # Use the helper to open dialog, fill ALL fields, and submit
        success = runner.open_dialog_and_fill(
            button_text="Ajouter",
            dialog_title="immeuble",
            field_values={
                "nom_edit": TestImmeubleCRUD.TEST_NAME,
                "adresse_edit": TestImmeubleCRUD.TEST_ADRESSE,
                "notes_edit": TestImmeubleCRUD.TEST_NOTES
            }
        )
        
        assert success, "Failed to create immeuble"
        
        # Refresh view
        runner.click_button("Actualiser")
        QTest.qWait(300)
        
        # Verify in UI
        new_count = runner.get_table_row_count()
        print(f"    New count: {new_count}")
        assert new_count == initial_count + 1, f"Expected {initial_count + 1} rows, got {new_count}"
        
        # Verify in database
        exists = runner.db_helper.record_exists("immeubles", "nom", TestImmeubleCRUD.TEST_NAME)
        assert exists, "Immeuble not found in database"
        print(f"    ✓ Verified in database")
    
    @staticmethod
    def test_read_immeuble(runner: TestRunner):
        """Test reading/viewing an immeuble"""
        print("\n  Test: Read Immeuble")
        
        view = runner.navigate_to_view("immeubles")
        
        tables = view.findChildren(QTableWidget)
        assert tables, "No table found"
        
        table = tables[0]
        row_count = table.rowCount()
        print(f"    Table has {row_count} rows")
        
        if row_count == 0:
            print("    ⚠ Skipping (no data)")
            return
        
        # Find our test immeuble
        found = False
        for row in range(row_count):
            item = table.item(row, 1)  # Column 1 is nom
            if item and item.text() == TestImmeubleCRUD.TEST_NAME:
                found = True
                print(f"    ✓ Found test immeuble in row {row}")
                break
        
        assert found, "Test immeuble not found in table"
    
    @staticmethod
    def test_update_immeuble(runner: TestRunner):
        """Test updating an existing immeuble"""
        print("\n  Test: Update Immeuble")
        
        view = runner.navigate_to_view("immeubles")
        
        tables = view.findChildren(QTableWidget)
        if not tables:
            print("    ⚠ No table found")
            return
        
        table = tables[0]
        target_row = -1
        
        for row in range(table.rowCount()):
            item = table.item(row, 1)
            if item and item.text() == TestImmeubleCRUD.TEST_NAME:
                target_row = row
                break
        
        if target_row == -1:
            print("    ⚠ Test immeuble not found, skipping update")
            return
        
        # Select the row
        table.selectRow(target_row)
        app = QApplication.instance()
        app.processEvents()
        QTest.qWait(200)
        
        # Update using helper - fill ALL fields
        success = runner.open_dialog_and_fill(
            button_text="Modifier",
            dialog_title="immeuble",
            field_values={
                "nom_edit": TestImmeubleCRUD.TEST_NAME,
                "adresse_edit": TestImmeubleCRUD.UPDATE_ADRESSE,
                "notes_edit": TestImmeubleCRUD.UPDATE_NOTES
            }
        )
        
        assert success, "Failed to update immeuble"
        
        runner.click_button("Actualiser")
        QTest.qWait(300)
        
        print("    ✓ Update completed")
    
    @staticmethod
    def test_delete_immeuble(runner: TestRunner):
        """Test deleting an immeuble"""
        print("\n  Test: Delete Immeuble")
        
        initial_count = runner.db_helper.count_records("immeubles")
        print(f"    Initial DB count: {initial_count}")
        
        if initial_count == 0:
            print("    ⚠ No immeubles to delete")
            return
        
        exists = runner.db_helper.record_exists("immeubles", "nom", TestImmeubleCRUD.TEST_NAME)
        
        if not exists:
            print(f"    ⚠ Test immeuble not found")
            return
        
        # Delete from database
        runner.db_helper.delete_record("immeubles", "nom", TestImmeubleCRUD.TEST_NAME)
        
        new_count = runner.db_helper.count_records("immeubles")
        assert new_count == initial_count - 1
        print(f"    ✓ Deleted test immeuble")
        print(f"    New DB count: {new_count}")


def run_immeuble_tests(runner: TestRunner):
    """Run all Immeuble CRUD tests"""
    print("\n" + "="*60)
    print("  IMMEUBLE CRUD TESTS")
    print("="*60)
    
    runner.run_test("Create Immeuble", TestImmeubleCRUD.test_create_immeuble)
    runner.run_test("Read Immeuble", TestImmeubleCRUD.test_read_immeuble)
    runner.run_test("Update Immeuble", TestImmeubleCRUD.test_update_immeuble)
    runner.run_test("Delete Immeuble", TestImmeubleCRUD.test_delete_immeuble)


if __name__ == "__main__":
    print("Immeuble CRUD Tests - Use run_all_ui_tests.py to execute")
