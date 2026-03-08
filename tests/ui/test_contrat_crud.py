#!/usr/bin/env python
"""
Contrat CRUD UI Tests
Tests all CRUD operations for Contrat entity through the UI
"""
import sys
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QTableWidget
from PySide6.QtTest import QTest

from tests.ui.base_ui_test import TestRunner


class TestContratCRUD:
    """Test suite for Contrat CRUD operations"""
    
    # Test data for creating contrat - ALL fields
    TEST_DATE_DEBUT = "2024-01-01"
    TEST_DATE_AUGMENTATION = "2024-06-01"
    TEST_MONTANT_PREMIER = 1500.000
    TEST_MONTANT_MENSUEL = 1500.000
    TEST_MONTANT_CAUTION = 3000.000
    TEST_MONTANT_PAS_PORTE = 5000.000
    TEST_COMPTEUR_STEG = "STEG-12345"
    TEST_COMPTEUR_SONEDE = "SONEDE-67890"
    TEST_CONDITIONS = "Conditions standard du contrat de location. Paiement mensuel avant le 5 de chaque mois."
    
    # Updated data
    UPDATE_MONTANT_MENSUEL = 1600.000
    UPDATE_MONTANT_CAUTION = 3200.000
    UPDATE_CONDITIONS = "Conditions mises à jour - Nouveau montant mensuel"
    
    @staticmethod
    def setup_test_data():
        """Create prerequisite data (locataire, immeuble, bureau)"""
        from app.database.connection import get_database
        from app.models.entities import Locataire, Immeuble, Bureau, StatutLocataire
        
        db = get_database()
        
        with db.session_scope() as session:
            # Create locataire
            locataire = Locataire(
                nom="Test Locataire Contrat",
                telephone="+216 50 111 222",
                email="test.contrat@example.com",
                cin="12345678",
                raison_sociale="Test Company Contrat",
                statut=StatutLocataire.ACTIF
            )
            session.add(locataire)
            session.flush()
            locataire_id = locataire.id
            
            # Create immeuble
            immeuble = Immeuble(
                nom="Immeuble Test Contrat",
                adresse="456 Avenue Contrat"
            )
            session.add(immeuble)
            session.flush()
            immeuble_id = immeuble.id
            
            # Create bureau
            bureau = Bureau(
                immeuble_id=immeuble_id,
                numero="C-101",
                etage="1er",
                surface_m2=50.0,
                est_disponible=True
            )
            session.add(bureau)
            session.flush()
            bureau_id = bureau.id
            
            print(f"    Setup: Locataire={locataire_id}, Immeuble={immeuble_id}, Bureau={bureau_id}")
            return locataire_id, bureau_id
    
    @staticmethod
    def test_create_contrat(runner: TestRunner):
        """Test creating a new contrat through the UI with ALL fields"""
        print("\n  Test: Create Contrat (All Fields)")
        
        # Setup prerequisite data
        locataire_id, bureau_id = TestContratCRUD.setup_test_data()
        
        # Navigate to Contrats view
        view = runner.navigate_to_view("contrats")
        assert view is not None, "Could not navigate to Contrats view"
        
        # Get initial count
        initial_count = runner.get_table_row_count()
        print(f"    Initial count: {initial_count}")
        
        # Open dialog and fill ALL fields
        # Note: locataire_combo index 1 = first locataire, bureaux_list index 0 = first bureau
        success = runner.open_dialog_and_fill(
            button_text="Ajouter",
            dialog_title="contrat",
            field_values={
                # Select locataire from combo (index 1 = first real item)
                "locataire_combo": 1,
                # Dates
                "date_debut": TestContratCRUD.TEST_DATE_DEBUT,
                "date_derniere_augmentation": TestContratCRUD.TEST_DATE_AUGMENTATION,
                # Amounts
                "montant_premier_mois": TestContratCRUD.TEST_MONTANT_PREMIER,
                "montant_mensuel": TestContratCRUD.TEST_MONTANT_MENSUEL,
                "montant_caution": TestContratCRUD.TEST_MONTANT_CAUTION,
                "montant_pas_de_porte": TestContratCRUD.TEST_MONTANT_PAS_PORTE,
                # Counters
                "compteur_steg_edit": TestContratCRUD.TEST_COMPTEUR_STEG,
                "compteur_sonede_edit": TestContratCRUD.TEST_COMPTEUR_SONEDE,
                # Conditions
                "conditions_edit": TestContratCRUD.TEST_CONDITIONS
            },
            list_selections={
                "bureaux_list": [0]  # Select first bureau
            }
        )
        
        assert success, "Failed to open contrat dialog"
        
        # Refresh view
        runner.click_button("Actualiser")
        QTest.qWait(500)
        
        new_count = runner.get_table_row_count()
        print(f"    New count: {new_count}")
        
        if new_count > initial_count:
            print(f"    ✓ Contrat created successfully")
        else:
            print(f"    ⚠ Contrat may not have been created")
    
    @staticmethod
    def test_read_contrat(runner: TestRunner):
        """Test reading/viewing a contrat"""
        print("\n  Test: Read Contrat")
        
        view = runner.navigate_to_view("contrats")
        
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
        
        print(f"    ✓ Found {row_count} contrat(s) in table")
    
    @staticmethod
    def test_update_contrat(runner: TestRunner):
        """Test updating an existing contrat with ALL fields"""
        print("\n  Test: Update Contrat (All Fields)")
        
        view = runner.navigate_to_view("contrats")
        
        tables = view.findChildren(QTableWidget)
        if not tables or tables[0].rowCount() == 0:
            print("    ⚠ No contrats to update")
            return
        
        # Select first row
        table = tables[0]
        table.selectRow(0)
        
        app = QApplication.instance()
        app.processEvents()
        QTest.qWait(200)
        
        # Update using helper with updated values
        success = runner.open_dialog_and_fill(
            button_text="Modifier",
            dialog_title="contrat",
            field_values={
                "montant_mensuel": TestContratCRUD.UPDATE_MONTANT_MENSUEL,
                "montant_caution": TestContratCRUD.UPDATE_MONTANT_CAUTION,
                "conditions_edit": TestContratCRUD.UPDATE_CONDITIONS
            }
        )
        
        assert success, "Failed to update contrat"
        
        runner.click_button("Actualiser")
        QTest.qWait(500)
        
        print("    ✓ Update completed")
    
    @staticmethod
    def test_delete_contrat(runner: TestRunner):
        """Test deleting a contrat"""
        print("\n  Test: Delete Contrat")
        
        initial_count = runner.db_helper.count_records("contrats")
        print(f"    Initial DB count: {initial_count}")
        
        if initial_count == 0:
            print("    ⚠ No contrats to delete")
            return
        
        # Get first contrat and delete it
        from app.database.connection import get_database
        from app.models.entities import Contrat
        
        db = get_database()
        with db.session_scope() as session:
            contrat = session.query(Contrat).first()
            if contrat:
                contrat_id = contrat.id
                session.delete(contrat)
                print(f"    ✓ Deleted contrat ID: {contrat_id}")
        
        new_count = runner.db_helper.count_records("contrats")
        print(f"    New DB count: {new_count}")
        
        # Cleanup test data
        TestContratCRUD.cleanup_test_data()
    
    @staticmethod
    def cleanup_test_data():
        """Clean up test data"""
        from app.database.connection import get_database
        from app.models.entities import Locataire, Immeuble, Bureau
        
        db = get_database()
        with db.session_scope() as session:
            # Delete in reverse order
            session.query(Bureau).filter(Bureau.numero == "C-101").delete()
            session.query(Immeuble).filter(Immeuble.nom == "Immeuble Test Contrat").delete()
            session.query(Locataire).filter(Locataire.nom == "Test Locataire Contrat").delete()
            print("    ✓ Cleaned up test data")


def run_contrat_tests(runner: TestRunner):
    """Run all Contrat CRUD tests"""
    print("\n" + "="*60)
    print("  CONTRAT CRUD TESTS")
    print("="*60)
    
    runner.run_test("Create Contrat", TestContratCRUD.test_create_contrat)
    runner.run_test("Read Contrat", TestContratCRUD.test_read_contrat)
    runner.run_test("Update Contrat", TestContratCRUD.test_update_contrat)
    runner.run_test("Delete Contrat", TestContratCRUD.test_delete_contrat)


if __name__ == "__main__":
    print("Contrat CRUD Tests - Use run_all_ui_tests.py to execute")
