"""empty

Revision ID: 000000000000
Revises: 
Create Date: 2026-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '000000000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tables for Gestion Locative application
    
    # Create immeubles table
    op.create_table(
        'immeubles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom', sa.String(200), nullable=False),
        sa.Column('adresse', sa.String(500), nullable=True),
        sa.Column('nombre_bureaux', sa.Integer(), default=0),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create bureaux table
    op.create_table(
        'bureaux',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('immeuble_id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(50), nullable=False),
        sa.Column('etage', sa.String(50), nullable=True),
        sa.Column('surface_m2', sa.Float(), nullable=True),
        sa.Column('est_disponible', sa.Boolean(), default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['immeuble_id'], ['immeubles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('immeuble_id', 'numero', name='uq_immeuble_bureau_numero')
    )
    
    # Create locataires table
    op.create_table(
        'locataires',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('immeuble_id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(200), nullable=False),
        sa.Column('telephone', sa.String(50), nullable=True),
        sa.Column('email', sa.String(200), nullable=True),
        sa.Column('cin', sa.String(50), nullable=True),
        sa.Column('raison_sociale', sa.String(200), nullable=True),
        sa.Column('statut', sa.Enum('ACTIF', 'HISTORIQUE', name='statutlocataire'), default='ACTIF'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['immeuble_id'], ['immeubles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create contrats table
    op.create_table(
        'contrats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('locataire_id', sa.Integer(), nullable=False),
        sa.Column('bureau_id', sa.Integer(), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=True),
        sa.Column('date_derniere_augmentation', sa.Date(), nullable=True),
        sa.Column('montant_premier_mois', sa.Numeric(10, 3), nullable=False),
        sa.Column('montant_mensuel', sa.Numeric(10, 3), nullable=False),
        sa.Column('montant_caution', sa.Numeric(10, 3), default=0),
        sa.Column('montant_pas_de_porte', sa.Numeric(10, 3), default=0),
        sa.Column('compteur_steg', sa.String(100), nullable=True),
        sa.Column('compteur_sonede', sa.String(100), nullable=True),
        sa.Column('est_resilie_col', sa.Boolean(), default=False),
        sa.Column('date_resiliation', sa.Date(), nullable=True),
        sa.Column('motif_resiliation', sa.Text(), nullable=True),
        sa.Column('conditions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['locataire_id'], ['locataires.id'], ),
        sa.ForeignKeyConstraint(['bureau_id'], ['bureaux.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create paiements table
    op.create_table(
        'paiements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('locataire_id', sa.Integer(), nullable=False),
        sa.Column('contrat_id', sa.Integer(), nullable=False),
        sa.Column('type_paiement', sa.Enum('LOYER', 'CAUTION', 'PAS_DE_PORTE', 'AUTRE', name='typepaiement'), nullable=False),
        sa.Column('montant_total', sa.Numeric(10, 3), nullable=False),
        sa.Column('date_paiement', sa.Date(), nullable=False),
        sa.Column('date_debut_periode', sa.Date(), nullable=True),
        sa.Column('date_fin_periode', sa.Date(), nullable=True),
        sa.Column('commentaire', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['locataire_id'], ['locataires.id'], ),
        sa.ForeignKeyConstraint(['contrat_id'], ['contrats.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create recus table
    op.create_table(
        'recus',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('paiement_id', sa.Integer(), nullable=False),
        sa.Column('numero_recu', sa.String(50), nullable=False),
        sa.Column('contenu', sa.JSON(), nullable=True),
        sa.Column('chemin_fichier', sa.String(500), nullable=True),
        sa.Column('date_generation', sa.DateTime(), nullable=True),
        sa.Column('genere_automatiquement', sa.Boolean(), default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['paiement_id'], ['paiements.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('paiement_id'),
        sa.UniqueConstraint('numero_recu')
    )
    
    # Create templates_recu table
    op.create_table(
        'templates_recu',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom', sa.String(200), nullable=False),
        sa.Column('est_par_defaut', sa.Boolean(), default=False),
        sa.Column('contenu_html', sa.Text(), nullable=False),
        sa.Column('date_creation', sa.DateTime(), nullable=True),
        sa.Column('date_modification', sa.DateTime(), nullable=True),
        sa.Column('actif', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('table_nom', sa.String(100), nullable=False),
        sa.Column('entite_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('donnees_avant', sa.JSON(), nullable=True),
        sa.Column('donnees_apres', sa.JSON(), nullable=True),
        sa.Column('utilisateur', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop all tables
    op.drop_table('audit_logs')
    op.drop_table('templates_recu')
    op.drop_table('recus')
    op.drop_table('paiements')
    op.drop_table('contrats')
    op.drop_table('locataires')
    op.drop_table('bureaux')
    op.drop_table('immeubles')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS statutlocataire')
    op.execute('DROP TYPE IF EXISTS typepaiement')
