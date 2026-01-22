from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, Text, 
    ForeignKey, Enum, Numeric, Boolean, UniqueConstraint, Table
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.dialects.sqlite import JSON


class Base(DeclarativeBase):
    pass


# Association table for many-to-many relationship between Contrat and Bureau
contrat_bureau = Table(
    'contrat_bureau',
    Base.metadata,
    Column('contrat_id', Integer, ForeignKey('contrats.id'), primary_key=True),
    Column('bureau_id', Integer, ForeignKey('bureaux.id'), primary_key=True)
)


class TypePaiement(str, PyEnum):
    LOYER = "loyer"
    CAUTION = "caution"
    PAS_DE_PORTE = "pas_de_porte"
    AUTRE = "autre"


class StatutLocataire(str, PyEnum):
    ACTIF = "actif"
    HISTORIQUE = "historique"


class Immeuble(Base):
    __tablename__ = "immeubles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(200), nullable=False)
    adresse = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    bureaux = relationship("Bureau", back_populates="immeuble", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Immeuble(id={self.id}, nom='{self.nom}')>"


class Bureau(Base):
    __tablename__ = "bureaux"

    id = Column(Integer, primary_key=True, autoincrement=True)
    immeuble_id = Column(Integer, ForeignKey("immeubles.id"), nullable=False)
    numero = Column(String(50), nullable=False)
    etage = Column(String(50), nullable=True)
    surface_m2 = Column(Float, nullable=True)
    est_disponible = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    immeuble = relationship("Immeuble", back_populates="bureaux")
    contrats = relationship("Contrat", secondary=contrat_bureau, back_populates="bureaux")

    __table_args__ = (
        UniqueConstraint('immeuble_id', 'numero', name='uq_immeuble_bureau_numero'),
    )

    def __repr__(self):
        return f"<Bureau(id={self.id}, numero='{self.numero}', immeuble_id={self.immeuble_id})>"


class Locataire(Base):
    """Représente un locataire (actuel ou historique)"""
    __tablename__ = "locataires"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    nom = Column(String(200), nullable=False)
    telephone = Column(String(50), nullable=True)
    email = Column(String(200), nullable=True)
    cin = Column(String(50), nullable=True)
    raison_sociale = Column(String(200), nullable=True)
    
    # Statut
    statut = Column(Enum(StatutLocataire), default=StatutLocataire.ACTIF)
    
    # Métadonnées
    commentaires = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    contrats = relationship("Contrat", back_populates="locataire")
    paiements = relationship("Paiement", back_populates="locataire")

    def __repr__(self):
        return f"<Locataire(id={self.id}, nom='{self.nom}', statut={self.statut})>"


class Contrat(Base):
    """Contrat de location pour un ou plusieurs bureaux"""
    __tablename__ = "contrats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    Locataire_id = Column(Integer, ForeignKey("locataires.id"), nullable=False)
    
    # Many-to-many relationship with Bureau
    bureaux = relationship("Bureau", secondary=contrat_bureau, back_populates="contrats")
    
    # Dates du contrat
    date_debut = Column(Date, nullable=False)
    date_derniere_augmentation = Column(Date, nullable=True)
    
    # Montants (total pour tous les bureaux)
    montant_premier_mois = Column(Numeric(10, 3), nullable=False)
    montant_mensuel = Column(Numeric(10, 3), nullable=False)
    montant_caution = Column(Numeric(10, 3), default=0)
    montant_pas_de_porte = Column(Numeric(10, 3), default=0)
    
    # Compteur
    compteur_steg = Column(String(100), nullable=True)
    compteur_sonede = Column(String(100), nullable=True)
    
    # Statut du contrat
    est_resilie_col = Column(Boolean, default=False)
    date_resiliation = Column(Date, nullable=True)
    motif_resiliation = Column(Text, nullable=True)
    
    # Métadonnées
    conditions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    locataire = relationship("Locataire", back_populates="contrats")
    paiements = relationship("Paiement", back_populates="contrat")

    def __repr__(self):
        return f"<Contrat(id={self.id}, Locataire_id={self.Locataire_id}, bureaux={len(self.bureaux)})>"

    @property
    def est_actif(self) -> bool:
        """Retourne True si le contrat est actuellement en cours"""
        est_resilie_val = getattr(self, 'est_resilie_col', None)
        if est_resilie_val is True:
            return False
        return True
    
    def get_numeros_bureaux(self) -> list:
        """Retourne la liste des numéros de bureaux"""
        return [b.numero for b in self.bureaux]


class Paiement(Base):
    """Enregistrement d'un paiement effectué par un locataire"""
    __tablename__ = "paiements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    Locataire_id = Column(Integer, ForeignKey("locataires.id"), nullable=False)
    contrat_id = Column(Integer, ForeignKey("contrats.id"), nullable=False)
    
    # Type et montant
    type_paiement = Column(Enum(TypePaiement), nullable=False)
    montant_total = Column(Numeric(10, 3), nullable=False)
    
    # Dates
    date_paiement = Column(Date, nullable=False)
    date_debut_periode = Column(Date, nullable=True)
    date_fin_periode = Column(Date, nullable=True)
    
    # Métadonnées
    commentaire = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    locataire = relationship("Locataire", back_populates="paiements")
    contrat = relationship("Contrat", back_populates="paiements")

    def __repr__(self):
        return f"<Paiement(id={self.id}, type={self.type_paiement}, montant={self.montant_total})>"

    def get_mois_couverts(self) -> list:
        type_paiement_val = getattr(self, 'type_paiement', None)
        if type_paiement_val != TypePaiement.LOYER:
            return []
        
        date_debut = self.date_debut_periode
        date_fin = self.date_fin_periode
        
        if date_debut is None or date_fin is None:
            return []
        
        mois_couverts = []
        current: date = date_debut
        end: date = date_fin
        
        while current <= end:
            mois_couverts.append((current.year, current.month))
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)
        
        return mois_couverts


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Action
    table_nom = Column(String(100), nullable=False)
    entite_id = Column(Integer, nullable=True)
    action = Column(String(50), nullable=False)

    # Données
    donnees_avant = Column(JSON, nullable=True)
    donnees_apres = Column(JSON, nullable=True)

    # Contexte
    utilisateur = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, table={self.table_nom})>"


class DocumentTreeConfig(Base):
    __tablename__ = "document_tree_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False, unique=True)
    tree_structure = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentTreeConfig(entity_type='{self.entity_type}')>"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    folder_path = Column(String(500), nullable=False)
    filename = Column(String(500), nullable=False)
    original_name = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Document(id={self.id}, entity_type='{self.entity_type}', entity_id={self.entity_id}, filename='{self.filename}')>"
