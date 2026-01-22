#!/usr/bin/env python
"""
Phase 2 - CRUD Operations Test Script
Tests all CRUD operations for the Gestion Locative application
"""
import sys
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_database
from app.models.entities import (
    Immeuble, Bureau, Locataire, Contrat, Paiement, 
    TypePaiement, StatutLocataire
)
from app.repositories import (
    ImmeubleRepository, BureauRepository, LocataireRepository,
    ContratRepository, PaiementRepository, ContratValidationError
)


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_immeuble_crud():
    """Test Immeuble CRUD operations"""
    print_section("IMMEUBLE CRUD")
    
    db = get_database()
    
    with db.session_scope() as session:
        repo = ImmeubleRepository(session)
        
        # Create
        print("\n1. Creation d'un immeuble...")
        immeuble = repo.create(
            nom="Immeuble Les Palmiers",
            adresse="45 Avenue Habib Bourguiba, Sfax",
            notes="Immeuble moderne avec parking"
        )
        print(f"   Cree: {immeuble}")
        
        immeuble_id = immeuble.id
        
        # Read
        print("\n2. Lecture...")
        immeuble_read = repo.get_by_id(immeuble_id)
        print(f"   Lu: {immeuble_read}")
        
        # Update
        print("\n3. Mise a jour...")
        repo.update(immeuble, adresse="45 Avenue Habib Bourguiba, Sfax (Updated)")
        print(f"   Mis a jour: {immeuble.adresse}")
        
        # List all
        print("\n4. Liste tous les immeubles:")
        for i in repo.get_all():
            print(f"   - {i.nom}")
        
        # Search
        print("\n5. Recherche 'Palmiers':")
        results = repo.search("Palmiers")
        for r in results:
            print(f"   - {r.nom}")
        
        return immeuble_id


def test_bureau_crud(immeuble_id: int):
    """Test Bureau CRUD operations"""
    print_section("BUREAU CRUD")
    
    db = get_database()
    
    with db.session_scope() as session:
        repo = BureauRepository(session)
        
        # Create multiple bureaux
        print("\n1. Creation de bureaux...")
        bureaux_data = [
            {"numero": "301", "etage": "3eme etage", "surface_m2": 60.0},
            {"numero": "302", "etage": "3eme etage", "surface_m2": 45.0},
            {"numero": "303", "etage": "3eme etage", "surface_m2": 120.0},
        ]
        
        created_ids = []
        for data in bureaux_data:
            bureau = repo.create(immeuble_id=immeuble_id, **data)
            created_ids.append(bureau.id)
            print(f"   Cree: Bureau {bureau.numero} - {bureau.surface_m2}m2")
        
        # Read
        print("\n2. Lecture...")
        bureau = repo.get_by_id(created_ids[0])
        print(f"   Lu: {bureau}")
        
        # Update
        print("\n3. Mise a jour disponibilite...")
        repo.update_disponibilite(bureau.id, False)
        print(f"   Bureau {bureau.numero} disponible: {bureau.est_disponible}")
        
        # Get by immeuble
        print("\n4. Bureaux par immeuble:")
        for b in repo.get_by_immeuble(immeuble_id):
            print(f"   - {b.numero} ({b.etage}) - Dispo: {b.est_disponible}")
        
        # Get disponibles
        print("\n5. Bureaux disponibles:")
        for b in repo.get_disponibles(immeuble_id):
            print(f"   - {b.numero}")
        
        return created_ids


def test_locataire_crud(immeuble_id: int):
    """Test Locataire CRUD operations"""
    print_section("LOCATAIRE CRUD")
    
    db = get_database()
    
    with db.session_scope() as session:
        repo = LocataireRepository(session)
        
        # Create
        print("\n1. Creation d'un locataire...")
        Locataire = repo.create(
            nom="Ahmed Ben Ahmed",
            telephone="+216 50 111 222",
            email="ahmed.benahmed@email.com",
            cin="12345678",
            raison_sociale="Cabinet d'Audit",
            statut=StatutLocataire.ACTIF
        )
        print(f"   Cree: {Locataire}")
        
        Locataire_id = Locataire.id
        
        # Read
        print("\n2. Lecture...")
        Locataire_read = repo.get_by_id(Locataire_id)
        print(f"   Lu: {Locataire_read}")
        
        # Update
        print("\n3. Mise a jour...")
        repo.update(Locataire, telephone="+216 50 999 888")
        print(f"   Telephone mis a jour: {Locataire.telephone}")
        
        # List all
        print("\n4. Liste tous les locataires:")
        for l in repo.get_all():
            print(f"   - {l.nom} ({l.statut})")
        
        # Get actifs
        print("\n5. Locataires actifs:")
        for l in repo.get_actifs():
            print(f"   - {l.nom}")
        
        # Search
        print("\n6. Recherche 'Ahmed':")
        results = repo.search("Ahmed")
        for r in results:
            print(f"   - {r.nom}")
        
        # Change statut
        print("\n7. Desactivation du Locataire...")
        repo.desactiver(Locataire_id)
        print(f"   Statut: {Locataire.statut}")
        
        return Locataire_id


def test_contrat_crud(locataire_id: int, bureau_ids: list):
    """Test Contrat CRUD operations with validation"""
    print_section("CONTRAT CRUD")
    
    db = get_database()
    
    with db.session_scope() as session:
        repo = ContratRepository(session)
        bureau_repo = BureauRepository(session)
        
        # Get bureau objects for the relation
        bureaux = [bureau_repo.get_by_id(bid) for bid in bureau_ids]
        
        # Create with validation
        print("\n1. Creation d'un contrat...")
        try:
            contrat, warnings = repo.create_with_validation(
                Locataire_id=locataire_id,
                date_debut=date(2024, 6, 1),
                montant_mensuel=Decimal("2500.000"),
                montant_premier_mois=Decimal("2500.000"),
                montant_caution=Decimal("5000.000"),
                date_derniere_augmentation=date(2024, 1, 1),
                bureaux=bureaux[:2]
            )
            print(f"   Cree: {contrat}")
            if warnings:
                print(f"   Avertissements: {warnings}")
            
            print(f"   Bureaux lies: {[b.numero for b in contrat.bureaux]}")
        except ContratValidationError as e:
            print(f"   Erreur de validation: {e.message}")
            return None
        
        contrat_id = contrat.id
        
        # Read
        print("\n2. Lecture...")
        contrat_read = repo.get_by_id(contrat_id)
        print(f"   Lu: {contrat_read}")
        
        # Get actifs
        print("\n3. Contrats actifs:")
        for c in repo.get_actifs():
            print(f"   - Contrat #{c.id} pour Locataire #{c.Locataire_id}")
        
        # Get by Locataire
        print("\n4. Contrats par Locataire:")
        for c in repo.get_by_locataire(locataire_id):
            print(f"   - #{c.id}: {c.date_debut} - {c.montant_mensuel}")
        
        # Add bureau to contrat
        print("\n5. Ajout d'un bureau au contrat...")
        if len(bureaux) > 2:
            repo.ajouter_bureau(contrat_id, bureaux[2])
            print(f"   Bureaux apres ajout: {[b.numero for b in contrat.bureaux]}")
        
        # Resilier contrat
        print("\n6. Resiliation du contrat...")
        repo.resilier(contrat_id, date_resiliation=date(2024, 12, 31), motif="Fin de contrat")
        print(f"   Resilie: {contrat.est_resilie_col}")
        print(f"   Date resiliation: {contrat.date_resiliation}")
        
        return contrat_id


def test_paiement_crud(locataire_id: int, contrat_id: int):
    """Test Paiement CRUD operations"""
    print_section("PAIEMENT CRUD")
    
    db = get_database()
    
    with db.session_scope() as session:
        repo = PaiementRepository(session)
        
        # Create caution payment
        print("\n1. Creation paiement caution...")
        paiement_caution = repo.create_paiement_autre(
            Locataire_id=locataire_id,
            contrat_id=contrat_id,
            type_paiement=TypePaiement.CAUTION,
            montant_total=Decimal("5000.000"),
            date_paiement=date(2024, 5, 25),
            commentaire="Paiement de la caution"
        )
        print(f"   Cree: {paiement_caution}")
        
        # Create rent payments
        print("\n2. Creation paiements loyer...")
        mois_noms = ['Janvier','Fevrier','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Decembre']
        for month in range(6, 10):
            paiement_loyer = repo.create_paiement_loyer(
                Locataire_id=locataire_id,
                contrat_id=contrat_id,
                montant_total=Decimal("2500.000"),
                date_paiement=date(2024, month, 1),
                date_debut_periode=date(2024, month, 1),
                date_fin_periode=date(2024, month, 30),
                commentaire=f"Loyer {mois_noms[month-1]} 2024"
            )
            print(f"   Cree: {paiement_loyer}")
        
        # List by contrat
        print("\n3. Paiements par contrat:")
        for p in repo.get_by_contrat(contrat_id):
            print(f"   - {p.type_paiement.value}: {p.montant_total} ({p.date_paiement})")
        
        # Get recent
        print("\n4. Paiements recents (30 jours):")
        for p in repo.get_recents(30):
            print(f"   - {p.date_paiement}: {p.montant_total}")
        
        # Get total rent paid
        print("\n5. Total loyers payes:")
        total = repo.get_total_loyers_payes(contrat_id)
        print(f"   Total: {total} TND")
        
        # Get unpaid months
        print("\n6. Mois impayes:")
        impayes = repo.get_loyers_impayes(contrat_id)
        for year, month in impayes:
            print(f"   - {mois_noms[month-1]} {year}")
        
        return True


def test_grille_calcul(locataire_id: int, contrat_id: int):
    """Test the red/green grid calculation logic"""
    print_section("GRILLE ROUGE/VERT (CALCULE)")
    
    db = get_database()
    
    with db.session_scope() as session:
        paiement_repo = PaiementRepository(session)
        contrat_repo = ContratRepository(session)
        
        contrat = contrat_repo.get_by_id(contrat_id)
        
        if contrat is None:
            print("Contrat non trouve")
            return
            
        print(f"\nContrat #{contrat.id} - Locataire: {contrat.locataire.nom}")
        print(f"Periode du contrat: {contrat.date_debut} a en cours")
        print(f"Mensuel: {contrat.montant_mensuel} TND")
        
        print("\n--- Grille des paiements (Rouge = Impaye, Vert = Paye) ---")
        
        paiements = paiement_repo.get_by_contrat_and_type(contrat_id, TypePaiement.LOYER)
        
        mois_couverts = set()
        for p in paiements:
            mois = p.get_mois_couverts()
            mois_couverts.update(mois)
            print(f"Paiement {p.date_paiement}: couvre {len(mois)} mois")
        
        print("\n2024:")
        print("Mois:      Jan  Fev  Mar  Avr  Mai  Jui  Jui  Aou  Sep  Oct  Nov  Dec")
        print("Statut:   ", end="")
        
        grid_line = ""
        for month in range(1, 13):
            if (2024, month) in mois_couverts:
                grid_line += " VER  "
            else:
                grid_line += " ROU  "
        print(grid_line)
        
        print(f"\nResume:")
        print(f"  - Mois couverts: {len(mois_couverts)}")
        print(f"  - Total paye: {paiement_repo.get_total_loyers_payes(contrat_id, 2024)} TND")


def main():
    """Run all CRUD tests"""
    print("=" * 60)
    print("  PHASE 2 - TESTS CRUD")
    print("  Application Gestion Locative Pro")
    print("=" * 60)
    
    try:
        immeuble_id = test_immeuble_crud()
        bureau_ids = test_bureau_crud(immeuble_id)
        Locataire_id = test_locataire_crud(immeuble_id)
        contrat_id = test_contrat_crud(Locataire_id, bureau_ids)
        
        if contrat_id:
            test_paiement_crud(Locataire_id, contrat_id)
            test_grille_calcul(Locataire_id, contrat_id)
        
        print("\n" + "=" * 60)
        print("  TOUS LES TESTS REUSSIS!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
