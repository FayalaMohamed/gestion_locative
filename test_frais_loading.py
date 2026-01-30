#!/usr/bin/env python3
"""Test repository loading of frais fields"""
import sys
sys.path.insert(0, r'D:\code\locations')

from app.database.connection import get_database
from app.repositories.paiement_repository import PaiementRepository

db = get_database()
session = db.get_session()

try:
    repo = PaiementRepository(session)
    
    # Test get_by_id for payment ID 2 (which has frais)
    p = repo.get_by_id(2)
    if p:
        print(f"Payment ID 2 loaded:")
        print(f"  Type: {p.type_paiement.value}")
        print(f"  Montant: {p.montant_total}")
        print(f"  frais_menage: {p.frais_menage} (type: {type(p.frais_menage)})")
        print(f"  frais_sonede: {p.frais_sonede} (type: {type(p.frais_sonede)})")
        print(f"  frais_steg: {p.frais_steg} (type: {type(p.frais_steg)})")
        print(f"  Has attr frais_menage: {hasattr(p, 'frais_menage')}")
        print(f"  Has attr frais_sonede: {hasattr(p, 'frais_sonede')}")
        print(f"  Has attr frais_steg: {hasattr(p, 'frais_steg')}")
        
        # Now test receipt service
        print("\n\nTesting ReceiptService:")
        from app.services.receipt_service import ReceiptService
        
        service = ReceiptService(session)
        pdf, receipt_num = service.generate_receipt(2)
        print(f"Receipt generated: {receipt_num}")
        print(f"PDF size: {len(pdf)} bytes")
        
        # Save PDF for inspection
        with open('test_receipt.pdf', 'wb') as f:
            f.write(pdf)
        print("PDF saved to test_receipt.pdf")
    else:
        print("Payment not found!")
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
finally:
    session.close()
    db.close()
