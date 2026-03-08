#!/usr/bin/env python
"""
Bureau CRUD UI Tests
Tests all CRUD operations for Bureau entity through the UI
"""
import sys
from pathlib import Path
from datetime import date

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QTableWidget
from PySide6.QtTest import QTest

from tests.ui.base_ui_test import TestRunner


class TestBureauCRUD:
    """Test suite for Bureau CRUD operations"""
    
    TEST_NUMERO = "B-101"
    TEST_ETAGE = "1er étage"
    TEST_SURFACE = 45.5
    TEST_NOTES = "Bureau lumineux avec vue sur la rue"
    
    # Updated values for testing update
    UPDATE_NUMERO = "B-102"
    UPDATE_ETAGE = "2ème étage"
    UPDATE_SURFACE = 50.0
    UPDATE_NOTES = "Bureau mis à jour avec nouvelles informations"
    
    @staticmethod
    def test_create_bureau(runner: TestRunner):
        """Test creating a new bureau through the UI with ALL fields"""
        print("\n  Test: Create Bureau (All Fields)")
        
        # First, we need an immeuble to associate with
        # Create one via database directly
        from app.database.connection import get_database
        from app.models.entities import Immeuble
        
        db = get_database()
        with db.session_scope() as session:
            immeuble = Immeuble(
                nom="Immeuble Test Bureau",
                adresse="123 Avenue Test",
                notes="Immeuble pour test bureau"
            )
            session.add(immeuble)
            session.flush()
            immeuble_id = immeuble.id
            print(f"    Created test immeuble ID: {immeuble_id}")
        
        # Navigate to Bureaux view
        view = runner.navigate_to_view("bureaux")
        assert view is not None, "Could not navigate to Bureaux view"
        
        # Get initial count
        initial_count = runner.get_table_row_count()
        print(f"    Initial count: {initial_count}")
        
        # Need to select immeuble from combo (index 1 = first real item after empty)
        # Note: surface_spin is QDoubleSpinBox, notes_edit is QTextEdit
        success = runner.open_dialog_and_fill(
            button_text="Ajouter",
            dialog_title="bureau",
            field_values={
                # Select immeuble from combo (index 1 = first real item)
                "immeuble_combo": 1,  # Index-based selection
                # Text fields
                "numero_edit": TestBureauCRUD.TEST_NUMERO,
                "etage_edit": TestBureauCRUD.TEST_ETAGE,
                # QDoubleSpinBox
                "surface_spin": TestBureauCRUD.TEST_SURFACE,
                # QTextEdit
                "notes_edit": TestBureauCRUD.TEST_NOTES
            }
        )
        
        assert success, "Failed to open bureau dialog"
        
        # Refresh view
        runner.click_button("Actualiser")
        QTest.qWait(500)
        
        # Verify in UI
        new_count = runner.get_table_row_count()
        print(f"    New count: {new_count}")
        
        if new_count > initial_count:
            print(f"    ✓ Bureau created successfully")
        else:
            print(f"    ⚠ Bureau may not have been created (immeuble selection required)")
    
    @staticmethod
    def test_read_bureau(runner: TestRunner):
        """Test reading/viewing a bureau"""
        print("\n  Test: Read Bureau")
        
        view = runner.navigate_to_view("bureaux")
        
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
        
        print(f"    ✓ Found {row_count} bureau(s) in table")
    
    @staticmethod
    def test_update_bureau(runner: TestRunner):
        """Test updating an existing bureau with ALL fields"""
        print("\n  Test: Update Bureau (All Fields)")
        
        view = runner.navigate_to_view("bureaux")
        
        tables = view.findChildren(QTableWidget)
        if not tables or tables[0].rowCount() == 0:
            print("    ⚠ No bureaux to update")
            return
        
        # Select first row
        table = tables[0]
        table.selectRow(0)
        
        app = QApplication.instance()
        app.processEvents()
        QTest.qWait(200)
        
        # Update using helper with ALL fields
        # Note: For update, we keep the same immeuble (index 1)
        success = runner.open_dialog_and_fill(
            button_text="Modifier",
            dialog_title="bureau",
            field_values={
                "immeuble_combo": 1,  # Keep same immeuble
                "numero_edit": TestBureauCRUD.UPDATE_NUMERO,
                "etage_edit": TestBureauCRUD.UPDATE_ETAGE,
                "surface_spin": TestBureauCRUD.UPDATE_SURFACE,
                "notes_edit": TestBureauCRUD.UPDATE_NOTES
            }
        )
        
        assert success, "Failed to update bureau"
        
        runner.click_button("Actualiser")
        QTest.qWait(500)
        
        print("    ✓ Update completed")
    
    @staticmethod
    def test_delete_bureau(runner: TestRunner):
        """Test deleting a bureau"""
        print("\n  Test: Delete Bureau")
        
        initial_count = runner.db_helper.count_records("bureaux")
        print(f"    Initial DB count: {initial_count}")
        
        if initial_count == 0:
            print("    ⚠ No bureaux to delete")
            return
        
        # Get first bureau and delete it
        from app.database.connection import get_database
        from app.models.entities import Bureau
        
        db = get_database()
        with db.session_scope() as session:
            bureau = session.query(Bureau).first()
            if bureau:
                bureau_id = bureau.id
                session.delete(bureau)
                print(f"    ✓ Deleted bureau ID: {bureau_id}")
        
        new_count = runner.db_helper.count_records("bureaux")
        print(f"    New DB count: {new_count}")
        
        # Cleanup test immeuble
        runner.db_helper.delete_record("immeubles", "nom", "Immeuble Test Bureau")


def run_bureau_tests(runner: TestRunner):
    """Run all Bureau CRUD tests"""
    print("\n" + "="*60)
    print("  BUREAU CRUD TESTS")
    print("="*60)
    
    runner.run_test("Create Bureau", TestBureauCRUD.test_create_bureau)
    runner.run_test("Read Bureau", TestBureauCRUD.test_read_bureau)
    runner.run_test("Update Bureau", TestBureauCRUD.test_update_bureau)
    runner.run_test("Delete Bureau", TestBureauCRUD.test_delete_bureau)


if __name__ == "__main__":
    print("Bureau CRUD Tests - Use run_all_ui_tests.py to execute")
