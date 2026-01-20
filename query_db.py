from app.database.connection import get_database
from app.models.entities import Immeuble, Locataire, Contrat, Paiement

db = get_database()

with db.session_scope() as session:
    print("=== IMMEUBLES ===")
    for i in session.query(Immeuble).all():
        print(f"  - {i.nom} ({i.adresse})")
    
    print("\n=== LOCATAIRES ===")
    for l in session.query(Locataire).all():
        print(f"  - {l.nom} ({l.raison_sociale or 'Particulier'}) - Statut: {l.statut}")
    
    print("\n=== CONTRATS ===")
    for c in session.query(Contrat).all():
        print(f"  - Contrat #{c.id}: {c.date_debut} - Mensuel: {c.montant_mensuel}")
    
    print("\n=== PAIEMENTS ===")
    for p in session.query(Paiement).all():
        print(f"  - {p.type_paiement.value}: {p.montant_total} ({p.date_paiement})")