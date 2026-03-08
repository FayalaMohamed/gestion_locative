"""Rename columns and add indexes

Revision ID: 001
Revises: e23588e3971c
Create Date: 2026-03-08

"""
from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, Sequence[str], None] = 'e23588e3971c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Rename columns in contrats table
    op.alter_column('contrats', 'Locataire_id', new_column_name='locataire_id')
    op.alter_column('contrats', 'est_resilie_col', new_column_name='est_resilie')
    
    # Rename column in paiements table
    op.alter_column('paiements', 'Locataire_id', new_column_name='locataire_id')
    
    # Add indexes for locataires table
    op.create_index('idx_locataire_nom', 'locataires', ['nom'])
    op.create_index('idx_locataire_statut', 'locataires', ['statut'])
    op.create_index('idx_locataire_cin', 'locataires', ['cin'])
    op.create_index('idx_locataire_email', 'locataires', ['email'])
    
    # Add indexes for contrats table
    op.create_index('idx_contrat_locataire_id', 'contrats', ['locataire_id'])
    op.create_index('idx_contrat_est_resilie', 'contrats', ['est_resilie'])
    op.create_index('idx_contrat_date_debut', 'contrats', ['date_debut'])
    
    # Add indexes for paiements table
    op.create_index('idx_paiement_contrat_id', 'paiements', ['contrat_id'])
    op.create_index('idx_paiement_locataire_id', 'paiements', ['locataire_id'])
    op.create_index('idx_paiement_type', 'paiements', ['type_paiement'])
    op.create_index('idx_paiement_date', 'paiements', ['date_paiement'])
    
    # Add indexes for bureaux table
    op.create_index('idx_bureau_immeuble_id', 'bureaux', ['immeuble_id'])
    op.create_index('idx_bureau_disponible', 'bureaux', ['est_disponible'])
    
    # Add index for documents table
    op.create_index('idx_document_entity', 'documents', ['entity_type', 'entity_id'])
    
    # Note: SQLite doesn't support ALTER TABLE for foreign key constraints
    # The CASCADE behavior is handled at the application level in the models


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_document_entity', 'documents')
    op.drop_index('idx_bureau_disponible', 'bureaux')
    op.drop_index('idx_bureau_immeuble_id', 'bureaux')
    op.drop_index('idx_paiement_date', 'paiements')
    op.drop_index('idx_paiement_type', 'paiements')
    op.drop_index('idx_paiement_locataire_id', 'paiements')
    op.drop_index('idx_paiement_contrat_id', 'paiements')
    op.drop_index('idx_contrat_date_debut', 'contrats')
    op.drop_index('idx_contrat_est_resilie', 'contrats')
    op.drop_index('idx_contrat_locataire_id', 'contrats')
    op.drop_index('idx_locataire_email', 'locataires')
    op.drop_index('idx_locataire_cin', 'locataires')
    op.drop_index('idx_locataire_statut', 'locataires')
    op.drop_index('idx_locataire_nom', 'locataires')
    
    # Rename columns back
    op.alter_column('paiements', 'locataire_id', new_column_name='Locataire_id')
    op.alter_column('contrats', 'est_resilie', new_column_name='est_resilie_col')
    op.alter_column('contrats', 'locataire_id', new_column_name='Locataire_id')
