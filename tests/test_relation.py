"""Test script to verify the many-to-many relationship between Contrat and Bureau"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.database.connection import get_database
from app.models.entities import Immeuble, Bureau, Locataire, Contrat, Paiement

db = get_database()

with db.session_scope() as session:
    print("=== CONTRATS ET LEURS BUREAUX ===\n")
    
    for contrat in session.query(Contrat).all():
        print(f"Contrat #{contrat.id} - Locataire: {contrat.locataire.nom}")
        print(f"  Bureaux: {[b.numero for b in contrat.bureaux]}")
        print(f"  Mensuel: {contrat.montant_mensuel}")
        print(f"  Actif: {contrat.est_actif}")
        print()
    
    print("=== EXEMPLE: CONTRAT AVEC PLUSIEURS BUREAUX ===\n")
    
    # Get first two bureaux from the database
    bureaux = session.query(Bureau).limit(2).all()
    
    if len(bureaux) >= 2:
        bureau1 = bureaux[0]
        bureau2 = bureaux[1]
        print(f"Bureau 1: {bureau1.numero}, {bureau1.etage}")
        print(f"Bureau 2: {bureau2.numero}, {bureau2.etage}")
    else:
        print(f"Only {len(bureaux)} bureau(x) found in database")
