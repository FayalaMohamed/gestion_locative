#!/usr/bin/env python
"""Database initialization script for Gestion Locative application.

This script initializes the database, creates all tables, and optionally
seeds the database with initial data.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from decimal import Decimal

from app.database.connection import init_database
from app.models.entities import (
    Immeuble, Bureau, Locataire, Contrat, Paiement,
    TemplateRecu, TypePaiement, StatutLocataire
)


def create_sample_data() -> None:
    """Create sample data for testing"""
    db = init_database()
    
    with db.session_scope() as session:
        # Check if data already exists
        existing_immeuble = session.query(Immeuble).first()
        if existing_immeuble:
            print("Data already exists, skipping seed...")
            return
        
        print("Creating sample data...")
        
        # Create sample immeuble
        immeuble1 = Immeuble(
            nom="Immeuble Centre Ville",
            adresse="123 Avenue Habib Bourguiba, Tunis",
            notes="Immeuble moderne avec ascenseur"
        )
        session.add(immeuble1)
        session.flush()
        
        # Create sample bureaux
        bureau1 = Bureau(
            immeuble_id=immeuble1.id,
            numero="101",
            etage="1er étage",
            surface_m2=50.0,
            notes="Bureau spacieux avec vue sur rue"
        )
        bureau2 = Bureau(
            immeuble_id=immeuble1.id,
            numero="102",
            etage="1er étage",
            surface_m2=35.0
        )
        bureau3 = Bureau(
            immeuble_id=immeuble1.id,
            numero="201",
            etage="2ème étage",
            surface_m2=45.0
        )
        session.add_all([bureau1, bureau2, bureau3])
        session.flush()
        
        # Create sample locataires
        locataire1 = Locataire(
            nom="Mohamed Ben Ali",
            telephone="+216 98 123 456",
            email="mohamed.benali@email.com",
            cin="01234567",
            raison_sociale="Cabinet d'Expertise Comptable",
            statut=StatutLocataire.ACTIF,
            commentaires="Client fidèle depuis 2020"
        )
        locataire2 = Locataire(
            nom="Fatma Trabelsi",
            telephone="+216 55 987 654",
            email="fatma.trabelsi@email.com",
            cin="98765432",
            raison_sociale="Agence de Voyage",
            statut=StatutLocataire.ACTIF,
            commentaires="Agence recommandée par un partenaire"
        )
        session.add_all([locataire1, locataire2])
        session.flush()
        
        # Create sample contrats (avec plusieurs bureaux possibles)
        contrat1 = Contrat(
            Locataire_id=locataire1.id,
            date_debut=datetime(2024, 1, 1).date(),
            montant_premier_mois=Decimal("1500.000"),
            montant_mensuel=Decimal("1500.000"),
            montant_caution=Decimal("3000.000"),
            montant_pas_de_porte=Decimal("0.000"),
            compteur_steg="STEG-2024-001",
            compteur_sonede="SONEDE-2024-001",
            est_resilie_col=False,
            bureaux=[bureau1]
        )
        contrat2 = Contrat(
            Locataire_id=locataire2.id,
            date_debut=datetime(2024, 3, 15).date(),
            montant_premier_mois=Decimal("1800.000"),
            montant_mensuel=Decimal("1800.000"),
            montant_caution=Decimal("3600.000"),
            montant_pas_de_porte=Decimal("5000.000"),
            compteur_steg="STEG-2024-002",
            compteur_sonede="SONEDE-2024-002",
            est_resilie_col=False,
            bureaux=[bureau3]
        )
        session.add_all([contrat1, contrat2])
        session.flush()
        
        # Create sample payments
        paiement1 = Paiement(
            Locataire_id=locataire1.id,
            contrat_id=contrat1.id,
            type_paiement=TypePaiement.CAUTION,
            montant_total=Decimal("3000.000"),
            date_paiement=datetime(2023, 12, 28).date(),
            commentaire="Paiement de la caution"
        )
        paiement2 = Paiement(
            Locataire_id=locataire1.id,
            contrat_id=contrat1.id,
            type_paiement=TypePaiement.LOYER,
            montant_total=Decimal("1500.000"),
            date_paiement=datetime(2024, 1, 1).date(),
            date_debut_periode=datetime(2024, 1, 1).date(),
            date_fin_periode=datetime(2024, 1, 31).date(),
            commentaire="Loyer Janvier 2024"
        )
        paiement3 = Paiement(
            Locataire_id=locataire1.id,
            contrat_id=contrat1.id,
            type_paiement=TypePaiement.LOYER,
            montant_total=Decimal("1500.000"),
            date_paiement=datetime(2024, 2, 1).date(),
            date_debut_periode=datetime(2024, 2, 1).date(),
            date_fin_periode=datetime(2024, 2, 29).date(),
            commentaire="Loyer Février 2024"
        )
        session.add_all([paiement1, paiement2, paiement3])
        
        # Create default receipt template
        template = TemplateRecu(
            nom="Template Standard",
            est_par_defaut=True,
            contenu_html="""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 20px; }
        .company-name { font-size: 24px; font-weight: bold; }
        .receipt-title { font-size: 20px; color: #666; }
        .info-section { margin-bottom: 20px; }
        .info-label { font-weight: bold; color: #333; }
        .amount { font-size: 18px; font-weight: bold; color: #2e7d32; }
        .footer { margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <div class="company-name">{{company_name}}</div>
        <div class="receipt-title">REÇU DE PAIEMENT</div>
        <div>N° {{numero_recu}}</div>
    </div>
    
    <div class="info-section">
        <div><span class="info-label">Date:</span> {{date_paiement}}</div>
        <div><span class="info-label">Locataire:</span> {{nom_locataire}}</div>
        <div><span class="info-label">Immeuble:</span> {{nom_immeuble}}</div>
        <div><span class="info-label">Bureau:</span> {{numero_bureau}}</div>
    </div>
    
    <div class="info-section">
        <div><span class="info-label">Type de paiement:</span> {{type_paiement}}</div>
        {% if periode %}
        <div><span class="info-label">Période:</span> {{periode}}</div>
        {% endif %}
    </div>
    
    <div class="info-section">
        <div class="amount">Montant: {{montant}} TND</div>
    </div>
    
    <div class="footer">
        <div>Reçu généré le {{date_generation}}</div>
        <div>{{company_address}}</div>
        {% if company_phone %}<div>{{company_phone}}</div>{% endif %}
    </div>
</body>
</html>
            """,
            actif=True
        )
        session.add(template)
        
        print("Sample data created successfully!")


def init_db(include_sample_data: bool = False) -> None:
    """Initialize the database"""
    print(f"Initializing database...")
    
    # Initialize database and create tables
    db = init_database()
    
    print(f"Database created at: {db.engine.url}")
    
    if include_sample_data:
        create_sample_data()
    else:
        print("Database initialized. Use --seed to create sample data.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization for Gestion Locative")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Create sample data after initialization"
    )
    
    args = parser.parse_args()
    
    try:
        init_db(include_sample_data=args.seed)
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
