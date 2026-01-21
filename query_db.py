#!/usr/bin/env python
"""
Query script to visualize database contents
Run: python query_db.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_database
from app.models.entities import (
    Immeuble, Bureau, Locataire, Contrat, Paiement,
    TypePaiement, StatutLocataire
)


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def query_immeubles(db):
    print_section("IMMEUBLES")
    
    with db.session_scope() as session:
        immeubles = session.query(Immeuble).all()
        
        print(f"\nTotal: {len(immeubles)} immeuble(s)\n")
        
        for i in immeubles:
            print(f"ID: {i.id}")
            print(f"  Nom: {i.nom}")
            print(f"  Adresse: {i.adresse or 'N/A'}")
            print(f"  Notes: {i.notes or 'N/A'}")
            print()


def query_bureaux(db):
    print_section("BUREAUX")
    
    with db.session_scope() as session:
        bureaux = session.query(Bureau).all()
        
        print(f"\nTotal: {len(bureaux)} bureau(x)\n")
        
        for b in bureaux:
            print(f"ID: {b.id} - Bureau #{b.numero}")
            print(f"  Immeuble ID: {b.immeuble_id}")
            print(f"  Etage: {b.etage or 'N/A'}")
            print(f"  Surface: {b.surface_m2 or 'N/A'} m2")
            print()


def query_locataires(db):
    print_section("LOCATAIRES")
    
    with db.session_scope() as session:
        locataires = session.query(Locataire).all()
        
        print(f"\nTotal: {len(locataires)} locataire(s)\n")
        
        for l in locataires:
            print(f"ID: {l.id}")
            print(f"  Nom: {l.nom}")
            print(f"  Email: {l.email or 'N/A'}")
            print(f"  Telephone: {l.telephone or 'N/A'}")
            print(f"  CIN: {l.cin or 'N/A'}")
            print(f"  Raison sociale: {l.raison_sociale or 'N/A'}")
            print(f"  Statut: {l.statut.value}")
            
            # Get associated immeuble(s) through contrats
            immeuble_ids = set()
            for contrat in l.contrats:
                for bureau in contrat.bureaux:
                    if bureau.immeuble_id:
                        immeuble_ids.add(bureau.immeuble_id)
            
            if immeuble_ids:
                print(f"  Immeuble ID(s): {', '.join(map(str, sorted(immeuble_ids)))}")
            else:
                print(f"  Immeuble ID(s): N/A")
            print()


def query_contrats(db):
    print_section("CONTRATS")
    
    with db.session_scope() as session:
        contrats = session.query(Contrat).all()
        
        print(f"\nTotal: {len(contrats)} contrat(s)\n")
        
        for c in contrats:
            print(f"ID: {c.id}")
            print(f"  Locataire ID: {c.Locataire_id}")
            
            # Get Locataire name
            Locataire_obj = session.query(Locataire).filter(Locataire.id == c.Locataire_id).first()
            if Locataire_obj:
                print(f"  Locataire: {Locataire_obj.nom}")
            
            # Get linked bureaux
            numeros_bureaux = [b.numero for b in c.bureaux]
            print(f"  Bureaux: {', '.join(numeros_bureaux) if numeros_bureaux else 'Aucun'}")
            
            print(f"  Date debut: {c.date_debut}")
            print(f"  Mensuel: {c.montant_mensuel} TND")
            print(f"  Caution: {c.montant_caution} TND")
            print(f"  Pas de porte: {c.montant_pas_de_porte} TND")
            print(f"  Resilie: {'Oui' if c.est_resilie_col else 'Non'}")
            print()


def query_paiements(db):
    print_section("PAIEMENTS")
    
    with db.session_scope() as session:
        paiements = session.query(Paiement).all()
        
        print(f"\nTotal: {len(paiements)} paiement(s)\n")
        
        for p in paiements:
            print(f"ID: {p.id}")
            print(f"  Locataire ID: {p.Locataire_id}")
            
            # Get Locataire name
            Locataire_obj = session.query(Locataire).filter(Locataire.id == p.Locataire_id).first()
            if Locataire_obj:
                print(f"  Locataire: {Locataire_obj.nom}")
            
            print(f"  Contrat ID: {p.contrat_id}")
            print(f"  Type: {p.type_paiement.value}")
            print(f"  Montant: {p.montant_total} TND")
            print(f"  Date paiement: {p.date_paiement}")
            
            if p.type_paiement == TypePaiement.LOYER:
                print(f"  Periode: {p.date_debut_periode} au {p.date_fin_periode}")
            
            print(f"  Commentaire: {p.commentaire or 'N/A'}")
            print()


def query_grille(db, contrat_id=1):
    print_section(f"GRILLE ROUGE/VERT - Contrat #{contrat_id}")
    
    with db.session_scope() as session:
        contrat = session.query(Contrat).filter(Contrat.id == contrat_id).first()
        
        if not contrat:
            print(f"Contrat #{contrat_id} non trouve")
            return
        
        # Get Locataire
        Locataire_obj = session.query(Locataire).filter(Locataire.id == contrat.Locataire_id).first()
        print(f"\nContrat #{contrat.id} - Locataire: {Locataire_obj.nom if Locataire_obj else 'N/A'}")
        print(f"Mensuel: {contrat.montant_mensuel} TND")
        
        # Get rent payments
        paiements_loyer = session.query(Paiement).filter(
            Paiement.contrat_id == contrat_id,
            Paiement.type_paiement == TypePaiement.LOYER
        ).all()
        
        # Build covered months
        mois_couverts = set()
        for p in paiements_loyer:
            mois = p.get_mois_couverts()
            mois_couverts.update(mois)
            print(f"Paiement {p.date_paiement}: couvre {len(mois)} mois")
        
        # Generate grid
        print(f"\n--- Grille des paiements ---")
        print("2024:")
        print("Mois:      Jan  Fev  Mar  Avr  Mai  Jui  Jui  Aou  Sep  Oct  Nov  Dec")
        print("Statut:   ", end="")
        
        grid = ""
        for month in range(1, 13):
            if (2024, month) in mois_couverts:
                grid += " VER  "
            else:
                grid += " ROU  "
        print(grid)
        
        print(f"\nTotal mois couverts: {len(mois_couverts)}")
        print(f"Total paye 2024: {sum(p.montant_total for p in paiements_loyer)} TND")


def main():
    """Main function to run all queries"""
    print("=" * 70)
    print("  GESTION LOCATIVE PRO - Base de Donnees")
    print("=" * 70)
    
    db = get_database()
    
    try:
        # Query all data
        query_immeubles(db)
        query_bureaux(db)
        query_locataires(db)
        query_contrats(db)
        query_paiements(db)
        
        # Query grille for contrat #1 (first contract)
        query_grille(db, contrat_id=1)
        
        print("\n" + "=" * 70)
        print("  Fin de la requete")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
