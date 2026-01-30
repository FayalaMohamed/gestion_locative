#!/usr/bin/env python3
"""Quick test to check if frais fields are loaded properly"""
import sys
sys.path.insert(0, r'D:\code\locations')

from app.database.connection import get_database
from app.repositories.paiement_repository import PaiementRepository
from app.models.entities import TypePaiement

db = get_database()
session = db.get_session()

try:
    repo = PaiementRepository(session)
    
    # Get all payments and check frais fields
    paiements = repo.get_all()
    print(f"Total payments: {len(paiements)}")
    print()
    
    for p in paiements:
        print(f"Payment ID: {p.id}")
        print(f"  Type: {p.type_paiement.value if p.type_paiement else 'None'}")
        print(f"  Montant total: {p.montant_total}")
        
        # Check if frais attributes exist
        has_menage = hasattr(p, 'frais_menage')
        has_sonede = hasattr(p, 'frais_sonede')
        has_steg = hasattr(p, 'frais_steg')
        
        print(f"  Has frais_menage attr: {has_menage}")
        print(f"  Has frais_sonede attr: {has_sonede}")
        print(f"  Has frais_steg attr: {has_steg}")
        
        if has_menage:
            print(f"  frais_menage value: {p.frais_menage}")
        if has_sonede:
            print(f"  frais_sonede value: {p.frais_sonede}")
        if has_steg:
            print(f"  frais_steg value: {p.frais_steg}")
        
        print("-" * 50)
        
        # Only show first 3 payments
        if p.id >= 3:
            break
    
    # Test get_by_id specifically
    if paiements:
        first_id = paiements[0].id
        print(f"\n\nTesting get_by_id({first_id}):")
        p2 = repo.get_by_id(first_id)
        if p2:
            print(f"  frais_menage: {p2.frais_menage}")
            print(f"  frais_sonede: {p2.frais_sonede}")
            print(f"  frais_steg: {p2.frais_steg}")
            print(f"  Type: {p2.type_paiement.value}")
            
            # Test receipt service
            print("\n\nTesting ReceiptService:")
            from app.services.receipt_service import ReceiptService
            service = ReceiptService(session)
            try:
                pdf, receipt_num = service.generate_receipt(first_id)
                print(f"  Receipt generated: {receipt_num}")
                print(f"  PDF size: {len(pdf)} bytes")
            except Exception as e:
                print(f"  Error: {e}")
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
finally:
    session.close()
    db.close()
