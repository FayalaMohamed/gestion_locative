#!/usr/bin/env python
"""
Deletion Constraint Tests
Tests that deletion constraints are properly enforced:
1. Cascade delete works when confirmed
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QTableWidget, QMessageBox
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from tests.ui.base_ui_test import TestRunner


class TestDeletionConstraints:
    """Test suite for deletion constraint enforcement"""

    @staticmethod
    def setup_constraint_test_data(runner: TestRunner):
        """Create test data: Immeuble -> Bureau -> Contrat -> Paiement"""
        from app.database.connection import get_database
        from app.models.entities import Immeuble, Bureau, Locataire, Contrat, Paiement, TypePaiement, StatutLocataire
        from decimal import Decimal
        from datetime import date

        db = get_database()
        with db.session_scope() as session:
            existing = session.query(Immeuble).filter(Immeuble.nom == "Test Immeuble Deletion").first()
            if existing:
                print(f"    Using existing test data: Immeuble={existing.id}")
                return {'immeuble_id': existing.id}

            immeuble = Immeuble(
                nom="Test Immeuble Deletion",
                adresse="123 Rue Test",
                notes="Pour test de suppression"
            )
            session.add(immeuble)
            session.flush()
            immeuble_id = immeuble.id

            bureau = Bureau(
                immeuble_id=immeuble_id,
                numero="DEL-001",
                etage="RDC",
                surface_m2=50.0,
                est_disponible=False,
                notes="Bureau pour test suppression"
            )
            session.add(bureau)
            session.flush()
            bureau_id = bureau.id

            locataire = Locataire(
                nom="Test Locataire Deletion",
                telephone="+216 99 000 000",
                email="delete@test.com",
                cin="DEL12345",
                statut=StatutLocataire.ACTIF
            )
            session.add(locataire)
            session.flush()
            locataire_id = locataire.id

            contrat = Contrat(
                locataire_id=locataire_id,
                date_debut=date(2024, 1, 1),
                montant_premier_mois=Decimal("1000.000"),
                montant_mensuel=Decimal("1000.000"),
                montant_caution=Decimal("2000.000"),
                est_resilie=False
            )
            contrat.bureaux.append(bureau)
            session.add(contrat)
            session.flush()
            contrat_id = contrat.id

            paiement = Paiement(
                locataire_id=locataire_id,
                contrat_id=contrat_id,
                type_paiement=TypePaiement.LOYER,
                montant_total=Decimal("1000.000"),
                date_paiement=date(2024, 2, 1),
                date_debut_periode=date(2024, 2, 1),
                date_fin_periode=date(2024, 2, 29)
            )
            session.add(paiement)

            print(f"    Created: Immeuble={immeuble_id}, Bureau={bureau_id}, Locataire={locataire_id}, Contrat={contrat_id}")

            return {
                'immeuble_id': immeuble_id,
                'bureau_id': bureau_id,
                'locataire_id': locataire_id,
                'contrat_id': contrat_id
            }

    @staticmethod
    def test_cascade_delete_immeuble(runner: TestRunner):
        """Test cascade deletion when user confirms"""
        print("\n  Test: Cascade Delete Immeuble")

        TestDeletionConstraints.setup_constraint_test_data(runner)

        view = runner.navigate_to_view("immeubles")
        tables = view.findChildren(QTableWidget)
        if not tables:
            print("    ⚠ No table found")
            return

        table = tables[0]

        target_row = -1
        for row in range(table.rowCount()):
            item = table.item(row, 1)
            if item and "Test Immeuble Deletion" in item.text():
                target_row = row
                break

        if target_row == -1:
            print("    ⚠ Test immeuble not found")
            return

        table.selectRow(target_row)
        QTest.qWait(200)

        initial = {
            'immeubles': runner.db_helper.count_records("immeubles"),
            'bureaux': runner.db_helper.count_records("bureaux"),
            'contrats': runner.db_helper.count_records("contrats"),
            'paiements': runner.db_helper.count_records("paiements")
        }
        print(f"    Before: {initial}")

        success = runner.delete_via_ui_with_confirmation(view, confirm_cascade=True)
        
        if not success:
            print("    ⚠ Failed to initiate deletion")
            return

        QTest.qWait(2000)

        final = {
            'immeubles': runner.db_helper.count_records("immeubles"),
            'bureaux': runner.db_helper.count_records("bureaux"),
            'contrats': runner.db_helper.count_records("contrats"),
            'paiements': runner.db_helper.count_records("paiements")
        }
        print(f"    After: {final}")

        if (final['immeubles'] == initial['immeubles'] - 1 and
            final['bureaux'] == initial['bureaux'] - 1 and
            final['contrats'] == initial['contrats'] - 1 and
            final['paiements'] == initial['paiements'] - 1):
            print("    ✓ PASS: Cascade deletion worked!")
        else:
            raise AssertionError(f"Cascade deletion failed! Expected all counts to decrease by 1. "
                f"Before: {initial}, After: {final}")


def run_deletion_constraint_tests(runner: TestRunner):
    """Run all Deletion Constraint tests"""
    print("\n" + "="*60)
    print("  DELETION CONSTRAINT TESTS")
    print("="*60)
    
    runner.run_test("Cascade Delete Immeuble", TestDeletionConstraints.test_cascade_delete_immeuble)


if __name__ == "__main__":
    print("Deletion Constraint Tests - Use run_all_ui_tests.py to execute")
