#!/usr/bin/env python3
"""Test repository loading of frais fields - avoiding circular imports"""
import sys
sys.path.insert(0, r'D:\code\locations')

# Import directly to avoid circular imports
from app.database.connection import get_database
from app.models.entities import Paiement
from sqlalchemy.orm import Session

db = get_database()
session = db.get_session()

try:
    # Direct query to avoid repository circular imports
    p = session.query(Paiement).filter(Paiement.id == 2).first()
    
    if p:
        print(f"Payment ID 2 loaded via direct query:")
        print(f"  Type: {p.type_paiement.value}")
        print(f"  Montant: {p.montant_total}")
        print(f"  frais_menage: {p.frais_menage} (type: {type(p.frais_menage)})")
        print(f"  frais_sonede: {p.frais_sonede} (type: {type(p.frais_sonede)})")
        print(f"  frais_steg: {p.frais_steg} (type: {type(p.frais_steg)})")
        
        # Test what happens when we do float conversion
        print(f"\nFloat conversions:")
        print(f"  float(p.frais_menage or 0): {float(p.frais_menage or 0)}")
        print(f"  float(p.frais_sonede or 0): {float(p.frais_sonede or 0)}")
        print(f"  float(p.frais_steg or 0): {float(p.frais_steg or 0)}")
        
        # Now test receipt service directly
        print("\n\nTesting ReceiptService logic:")
        
        # Simulate what receipt_service does
        payment_data = [
            ['Type de paiement:', 'Loyer'],
            ['Date de paiement:', p.date_paiement.strftime('%d/%m/%Y')],
            ['Montant total:', f"{float(p.montant_total):,.0f} TND"],
        ]
        
        # Add frais details for loyer payments
        if p.type_paiement.value == 'loyer':
            frais_menage = float(p.frais_menage or 0)
            frais_sonede = float(p.frais_sonede or 0)
            frais_steg = float(p.frais_steg or 0)
            
            print(f"  frais_menage value: {frais_menage}")
            print(f"  frais_sonede value: {frais_sonede}")
            print(f"  frais_steg value: {frais_steg}")
            
            if frais_menage > 0:
                payment_data.append(['Frais ménage:', f"{frais_menage:,.0f} TND"])
                print("  -> Added frais_menage to receipt")
            if frais_sonede > 0:
                payment_data.append(['Frais SONEDE (eau):', f"{frais_sonede:,.0f} TND"])
                print("  -> Added frais_sonede to receipt")
            if frais_steg > 0:
                payment_data.append(['Frais STEG (élec.):', f"{frais_steg:,.0f} TND"])
                print("  -> Added frais_steg to receipt")
        
        print(f"\nFinal payment_data for receipt:")
        for row in payment_data:
            print(f"  {row}")
    else:
        print("Payment not found!")
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
finally:
    session.close()
