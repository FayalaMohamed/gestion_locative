#!/usr/bin/env python
"""
Script to add 50 test tenants to verify scrolling functionality
"""
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import init_database
from app.models.entities import Locataire, Contrat, Bureau, Paiement, TypePaiement, StatutLocataire


def add_test_tenants():
    """Add 50 test tenants with contracts and payments"""
    db = init_database()
    
    with db.session_scope() as session:
        # Check if we already have many tenants
        existing_count = session.query(Locataire).count()
        if existing_count > 10:
            print(f"Already have {existing_count} tenants. Skipping...")
            return
        
        print(f"Adding 50 test tenants...")
        
        # Get existing immeuble and bureaux
        immeuble = session.query(Bureau).first()
        if not immeuble:
            print("No existing immeuble found. Please run init_db.py --seed first")
            return
        
        # Get first bureau
        bureau = session.query(Bureau).first()
        if not bureau:
            print("No existing bureau found. Please run init_db.py --seed first")
            return
        
        for i in range(1, 51):
            # Create locataire
            locataire = Locataire(
                nom=f"Locataire Test {i:02d}",
                telephone=f"+216 99 {i:03d} {i:03d}",
                email=f"locataire{i:02d}@test.com",
                cin=f"{i:08d}",
                raison_sociale=f"Entreprise Test {i:02d}",
                statut=StatutLocataire.ACTIF,
                commentaires=f"Client de test numéro {i}"
            )
            session.add(locataire)
            session.flush()  # Get the ID
            
            # Create contrat
            contrat = Contrat(
                Locataire_id=locataire.id,
                date_debut=datetime(2024, 1, 1).date(),
                montant_premier_mois=Decimal("1000.000"),
                montant_mensuel=Decimal("1000.000"),
                montant_caution=Decimal("2000.000"),
                montant_pas_de_porte=Decimal("0.000"),
                est_resilie_col=False,
                bureaux=[bureau]
            )
            session.add(contrat)
            session.flush()
            
            # Create a payment
            paiement = Paiement(
                Locataire_id=locataire.id,
                contrat_id=contrat.id,
                type_paiement=TypePaiement.LOYER,
                montant_total=Decimal("1050.000"),
                frais_menage=Decimal("50.000"),
                frais_sonede=Decimal("0.000"),
                frais_steg=Decimal("0.000"),
                date_paiement=datetime(2024, 1, 15).date(),
                date_debut_periode=datetime(2024, 1, 1).date(),
                date_fin_periode=datetime(2024, 1, 31).date(),
                commentaire=f"Loyer test pour locataire {i}"
            )
            session.add(paiement)
            
            if i % 10 == 0:
                print(f"  Added {i}/50 tenants...")
        
        print(f"✓ Successfully added 50 test tenants with contracts and payments!")
        print(f"Total tenants in database: {existing_count + 50}")


if __name__ == "__main__":
    try:
        add_test_tenants()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
