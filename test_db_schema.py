#!/usr/bin/env python3
"""Quick test to check if frais fields are loaded properly"""
import sys
sys.path.insert(0, r'D:\code\locations')

from sqlalchemy import create_engine, text
from app.utils.config import Config

config = Config()
engine = create_engine(f"sqlite+pysqlite:///{config.database_path}")

with engine.connect() as conn:
    # Check table schema
    result = conn.execute(text("PRAGMA table_info(paiements)"))
    columns = result.fetchall()
    print("Paiements table columns:")
    for col in columns:
        print(f"  {col}")
    
    # Check actual data
    result = conn.execute(text("SELECT id, type_paiement, montant_total, frais_menage, frais_sonede, frais_steg FROM paiements"))
    rows = result.fetchall()
    print("\n\nPaiements data:")
    for row in rows:
        print(f"  {row}")
