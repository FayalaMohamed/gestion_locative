#!/usr/bin/env python
"""Database initialization script for Gestion Locative application.

This script initializes the database, creates all tables, and optionally
seeds the database with initial data.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from decimal import Decimal

from alembic import command
from alembic.config import Config as AlembicConfig

from app.database.connection import init_database
from app.models.entities import (
    Immeuble, Bureau, Locataire, Contrat, Paiement,
    TypePaiement, StatutLocataire, DocumentTreeConfig
)


DB_PATH = project_root / "data" / "gestion_locative.db"
ALEMBIC_INI_PATH = project_root / "alembic.ini"


def create_empty_database() -> None:
    """Create an empty database with all tables using Alembic migrations.
    
    This function:
    1. Checks if database already exists and warns user
    2. Creates the data directory if it doesn't exist
    3. Runs alembic upgrade head to create all tables
    4. Does NOT add any sample data
    5. Prints success message with database path
    """
    # Check if database already exists
    if DB_PATH.exists():
        print(f"Warning: Database already exists at: {DB_PATH}")
        response = input("Do you want to recreate it? This will delete all existing data. [y/N]: ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return
        # Remove existing database
        DB_PATH.unlink()
        print("Existing database removed.")
    
    # Create data directory if it doesn't exist
    data_dir = DB_PATH.parent
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Data directory ready: {data_dir}")
    
    # Configure Alembic
    alembic_cfg = AlembicConfig(str(ALEMBIC_INI_PATH))
    
    # Run migrations to create all tables
    print("Running Alembic migrations...")
    command.upgrade(alembic_cfg, "head")
    
    # Print success message
    print(f"Empty database created successfully at: {DB_PATH}")


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
            montant_total=Decimal("1650.000"),
            frais_menage=Decimal("50.000"),
            frais_sonede=Decimal("50.000"),
            frais_steg=Decimal("50.000"),
            date_paiement=datetime(2024, 1, 1).date(),
            date_debut_periode=datetime(2024, 1, 1).date(),
            date_fin_periode=datetime(2024, 1, 31).date(),
            commentaire="Loyer Janvier 2024 avec frais"
        )
        paiement3 = Paiement(
            Locataire_id=locataire1.id,
            contrat_id=contrat1.id,
            type_paiement=TypePaiement.LOYER,
            montant_total=Decimal("1600.000"),
            frais_menage=Decimal("50.000"),
            frais_sonede=Decimal("50.000"),
            frais_steg=Decimal("0.000"),
            date_paiement=datetime(2024, 2, 1).date(),
            date_debut_periode=datetime(2024, 2, 1).date(),
            date_fin_periode=datetime(2024, 2, 29).date(),
            commentaire="Loyer Février 2024 avec frais ménage et eau"
        )
        session.add_all([paiement1, paiement2, paiement3])
        
        print("Sample data created successfully!")


def create_default_tree_configs() -> None:
    """Create default tree configurations for document management"""
    db = init_database()

    default_configs = {
        "immeuble": {"name": "Immeuble", "children": []},
        "bureau": {"name": "Bureau", "children": []},
        "locataire": {"name": "Locataire", "children": []},
        "contrat": {"name": "Contrat", "children": []},
        "paiement": {"name": "Paiement", "children": []}
    }

    with db.session_scope() as session:
        for entity_type, tree_structure in default_configs.items():
            existing = session.query(DocumentTreeConfig).filter(
                DocumentTreeConfig.entity_type == entity_type
            ).first()
            if not existing:
                config = DocumentTreeConfig(
                    entity_type=entity_type,
                    tree_structure=tree_structure
                )
                session.add(config)
        print("Default tree configurations created!")


def init_db(include_sample_data: bool = False) -> None:
    """Initialize the database"""
    print(f"Initializing database...")
    
    # Initialize database and create tables
    db = init_database()
    
    print(f"Database created at: {db.engine.url}")
    
    # Create default document tree configurations
    create_default_tree_configs()
    
    if include_sample_data:
        create_sample_data()
    else:
        print("Database initialized. Use --seed to create sample data.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization for Gestion Locative")
    
    # Create mutually exclusive group for --empty and --seed
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--empty",
        action="store_true",
        help="Create an empty database with all tables (no sample data)"
    )
    group.add_argument(
        "--seed",
        action="store_true",
        help="Create database with sample data"
    )
    
    args = parser.parse_args()
    
    try:
        if args.empty:
            # Create empty database using Alembic migrations
            create_empty_database()
            # Also create default tree configurations
            create_default_tree_configs()
        elif args.seed:
            # Create database with sample data
            init_db(include_sample_data=True)
        
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
