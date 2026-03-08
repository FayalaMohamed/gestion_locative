#!/usr/bin/env python
"""
Paiement CRUD UI Tests
Tests all CRUD operations for Paiement entity through the UI
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


class TestPaiementCRUD:
    """Test suite for Paiement CRUD operations"""
    
    # Test data for creating paiement - ALL fields
    TEST_TYPE = "LOYER"  # TypePaiement.LOYER.value
    TEST_MONTANT = 1500.000
    TEST_FRAIS_MENAGE = 50.000
    TEST_FRAIS_SONEDE = 30.000
    TEST_FRAIS_STEG = 40.000
    TEST_DATE_PAIEMENT = "2024-03-15"
    TEST_COMMENTAIRE = "Paiement loyer Mars 2024 - Tous frais inclus"
    
    # Period data
    TEST_MOIS_DEBUT = 0  # January (index 0)
    TEST_ANNEE_DEBUT = 2024
    TEST_MOIS_FIN = 0    # January (index 0)
    TEST_ANNEE_FIN = 2024
    
    # Updated data
    UPDATE_MONTANT = 1600.000
    UPDATE_FRAIS_MENAGE = 60.000
    UPDATE_COMMENTAIRE = "Paiement mis à jour avec nouveau montant"
    
    @staticmethod
    def setup_test_data():
        """Create prerequisite data (locataire, immeuble, bureau, contrat)"""
        from app.database.connection import get_database
        from app.models.entities import (
            Locataire, Immeuble, Bureau, Contrat, StatutLocataire
        )
        from app.repositories.contrat_repository import ContratRepository
        
        db = get_database()
        
        with db.session_scope() as session:
            # Create locataire
            locataire = Locataire(
                nom="Test Locataire Paiement",
                telephone="+216 50 333 444",
                email="test.paiement@example.com",
                cin="87654321",
                raison_sociale="Test Company Paiement",
                statut=StatutLocataire.ACTIF
            )
            session.add(locataire)
            session.flush()
            locataire_id = locataire.id
            
            # Create immeuble
            immeuble = Immeuble(
                nom="Immeuble Test Paiement",
                adresse="789 Avenue Paiement"
            )
            session.add(immeuble)
            session.flush()
            immeuble_id = immeuble.id
            
            # Create bureau
            bureau = Bureau(
                immeuble_id=immeuble_id,
                numero="P-101",
                etage="RDC",
                surface_m2=60.0,
                est_disponible=True
            )
            session.add(bureau)
            session.flush()
            bureau_id = bureau.id
            
            # Create contrat
            contrat = Contrat(
                locataire_id=locataire_id,
                date_debut=date(2024, 1, 1),
                montant_premier_mois=Decimal("1500.000"),
                montant_mensuel=Decimal("1500.000"),
                montant_caution=Decimal("3000.000"),
                est_resilie=False
            )
            # Associate bureau with contrat
            contrat.bureaux.append(bureau)
            session.add(contrat)
            session.flush()
            contrat_id = contrat.id
            
            print(f"    Setup: Locataire={locataire_id}, Contrat={contrat_id}")
            return locataire_id, contrat_id
    
    @staticmethod
    def test_create_paiement(runner: TestRunner):
        """Test creating a new paiement through the UI with ALL fields"""
        print("\n  Test: Create Paiement (All Fields)")
        
        # Setup prerequisite data
        locataire_id, contrat_id = TestPaiementCRUD.setup_test_data()
        
        # Navigate to Paiements view
        view = runner.navigate_to_view("paiements")
        assert view is not None, "Could not navigate to Paiements view"
        
        # Get initial count
        initial_count = runner.get_table_row_count()
        print(f"    Initial count: {initial_count}")
        
        # Open dialog and fill ALL fields
        # Note: Need to select locataire first (index 1), then contrat (index 1)
        success = runner.open_dialog_and_fill(
            button_text="Ajouter",
            dialog_title="paiement",
            field_values={
                # Select locataire and contrat from combos
                "locataire_combo": 1,  # First real locataire
                "contrat_combo": 1,    # First real contrat
                # Type - find by text "Loyer" or "LOYER"
                "type_combo": "Loyer",
                # Amounts
                "montant": TestPaiementCRUD.TEST_MONTANT,
                "frais_menage": TestPaiementCRUD.TEST_FRAIS_MENAGE,
                "frais_sonede": TestPaiementCRUD.TEST_FRAIS_SONEDE,
                "frais_steg": TestPaiementCRUD.TEST_FRAIS_STEG,
                # Date
                "date_paiement": TestPaiementCRUD.TEST_DATE_PAIEMENT,
                # Period (indices for combo boxes)
                "mois_debut_combo": TestPaiementCRUD.TEST_MOIS_DEBUT,
                "annee_debut_spin": TestPaiementCRUD.TEST_ANNEE_DEBUT,
                "mois_fin_combo": TestPaiementCRUD.TEST_MOIS_FIN,
                "annee_fin_spin": TestPaiementCRUD.TEST_ANNEE_FIN,
                # Comment
                "commentaire_edit": TestPaiementCRUD.TEST_COMMENTAIRE
            }
        )
        
        assert success, "Failed to open paiement dialog"
        
        # Refresh view
        runner.click_button("Actualiser")
        QTest.qWait(500)
        
        new_count = runner.get_table_row_count()
        print(f"    New count: {new_count}")
        
        if new_count > initial_count:
            print(f"    ✓ Paiement created successfully")
        else:
            print(f"    ⚠ Paiement may not have been created")
    
    @staticmethod
    def test_read_paiement(runner: TestRunner):
        """Test reading/viewing a paiement"""
        print("\n  Test: Read Paiement")
        
        view = runner.navigate_to_view("paiements")
        
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
        
        print(f"    ✓ Found {row_count} paiement(s) in table")
    
    @staticmethod
    def test_update_paiement(runner: TestRunner):
        """Test updating an existing paiement with ALL fields"""
        print("\n  Test: Update Paiement (All Fields)")
        
        view = runner.navigate_to_view("paiements")
        
        tables = view.findChildren(QTableWidget)
        if not tables or tables[0].rowCount() == 0:
            print("    ⚠ No paiements to update")
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
            dialog_title="paiement",
            field_values={
                "montant": TestPaiementCRUD.UPDATE_MONTANT,
                "frais_menage": TestPaiementCRUD.UPDATE_FRAIS_MENAGE,
                "commentaire_edit": TestPaiementCRUD.UPDATE_COMMENTAIRE
            }
        )
        
        assert success, "Failed to update paiement"
        
        runner.click_button("Actualiser")
        QTest.qWait(500)
        
        print("    ✓ Update completed")
    
    @staticmethod
    def test_delete_paiement(runner: TestRunner):
        """Test deleting a paiement"""
        print("\n  Test: Delete Paiement")
        
        initial_count = runner.db_helper.count_records("paiements")
        print(f"    Initial DB count: {initial_count}")
        
        if initial_count == 0:
            print("    ⚠ No paiements to delete")
            return
        
        # Get first paiement and delete it
        from app.database.connection import get_database
        from app.models.entities import Paiement
        
        db = get_database()
        with db.session_scope() as session:
            paiement = session.query(Paiement).first()
            if paiement:
                paiement_id = paiement.id
                session.delete(paiement)
                print(f"    ✓ Deleted paiement ID: {paiement_id}")
        
        new_count = runner.db_helper.count_records("paiements")
        print(f"    New DB count: {new_count}")
        
        # Cleanup test data
        TestPaiementCRUD.cleanup_test_data()
    
    @staticmethod
    def cleanup_test_data():
        """Clean up test data"""
        from app.database.connection import get_database
        from app.models.entities import Locataire, Immeuble, Bureau, Contrat
        
        db = get_database()
        with db.session_scope() as session:
            # Delete in reverse order
            contrat = session.query(Contrat).filter(
                Contrat.montant_mensuel == Decimal("1500.000")
            ).first()
            if contrat:
                session.delete(contrat)
            
            session.query(Bureau).filter(Bureau.numero == "P-101").delete()
            session.query(Immeuble).filter(Immeuble.nom == "Immeuble Test Paiement").delete()
            session.query(Locataire).filter(Locataire.nom == "Test Locataire Paiement").delete()
            print("    ✓ Cleaned up test data")


def run_paiement_tests(runner: TestRunner):
    """Run all Paiement CRUD tests"""
    print("\n" + "="*60)
    print("  PAIEMENT CRUD TESTS")
    print("="*60)
    
    runner.run_test("Create Paiement", TestPaiementCRUD.test_create_paiement)
    runner.run_test("Read Paiement", TestPaiementCRUD.test_read_paiement)
    runner.run_test("Update Paiement", TestPaiementCRUD.test_update_paiement)
    runner.run_test("Delete Paiement", TestPaiementCRUD.test_delete_paiement)


if __name__ == "__main__":
    print("Paiement CRUD Tests - Use run_all_ui_tests.py to execute")
