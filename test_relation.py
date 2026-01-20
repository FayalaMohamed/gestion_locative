"""Test script to verify the many-to-many relationship between Contrat and Bureau"""
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
    
    # Créer un contrat avec plusieurs bureaux pour démontrer
    bureau101 = session.query(Bureau).filter(Bureau.numero == "101").first()
    bureau102 = session.query(Bureau).filter(Bureau.numero == "102").first()
    
    print(f"Bureau 101: {bureau101.numero}, {bureau101.etage}")
    print(f"Bureau 102: {bureau102.numero}, {bureau102.etage}")
