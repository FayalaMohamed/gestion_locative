"""Locataire repository"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.entities import Locataire, StatutLocataire, Contrat, Bureau
from app.models.entities import contrat_bureau
from app.repositories.base import BaseRepository


class LocataireRepository(BaseRepository[Locataire]):
    """Repository for Locataire CRUD operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Locataire)
    
    def get_by_nom(self, nom: str) -> List[Locataire]:
        """Find locataires by name"""
        return self.session.query(Locataire).filter(
            Locataire.nom.ilike(f"%{nom}%")
        ).all()
    
    def get_actifs(self) -> List[Locataire]:
        """Get all active locataires"""
        return self.filter_by(statut=StatutLocataire.ACTIF)
    
    def get_historique(self) -> List[Locataire]:
        """Get all historical (inactive) locataires"""
        return self.filter_by(statut=StatutLocataire.HISTORIQUE)
    
    def get_by_immeuble(self, immeuble_id: int) -> List[Locataire]:
        """Get locataires who have contracts with offices in an immeuble"""
        return self.session.query(Locataire).join(
            Contrat, Locataire.id == Contrat.locataire_id
        ).join(
            contrat_bureau, Contrat.id == contrat_bureau.c.contrat_id
        ).join(
            Bureau, contrat_bureau.c.bureau_id == Bureau.id
        ).filter(
            Bureau.immeuble_id == immeuble_id
        ).distinct().all()
    
    def get_actifs_by_immeuble(self, immeuble_id: int) -> List[Locataire]:
        """Get active locataires who have active contracts with offices in an immeuble"""
        return self.session.query(Locataire).join(
            Contrat, Locataire.id == Contrat.locataire_id
        ).join(
            contrat_bureau, Contrat.id == contrat_bureau.c.contrat_id
        ).join(
            Bureau, contrat_bureau.c.bureau_id == Bureau.id
        ).filter(
            Bureau.immeuble_id == immeuble_id,
            Contrat.est_resilie == False,
            Locataire.statut == StatutLocataire.ACTIF
        ).distinct().all()
    
    def search(self, query: str) -> List[Locataire]:
        """Search locataires by name, email, phone, CIN or raison_sociale"""
        search_term = f"%{query}%"
        return self.session.query(Locataire).filter(
            (Locataire.nom.ilike(search_term)) |
            (Locataire.email.ilike(search_term)) |
            (Locataire.telephone.ilike(search_term)) |
            (Locataire.cin.ilike(search_term)) |
            (Locataire.raison_sociale.ilike(search_term))
        ).all()
    
    def get_by_cin(self, cin: str) -> Optional[Locataire]:
        """Find locataire by CIN"""
        return self.first(cin=cin)
    
    def get_by_email(self, email: str) -> Optional[Locataire]:
        """Find locataire by email"""
        return self.first(email=email)
    
    def change_statut(self, locataire_id: int, nouveau_statut: StatutLocataire) -> Optional[Locataire]:
        """Change Locataire status"""
        locataire = self.get_by_id(locataire_id)
        if locataire:
            locataire.statut = nouveau_statut
            self.session.flush()
        return locataire
    
    def desactiver(self, locataire_id: int) -> Optional[Locataire]:
        """Deactivate a Locataire (move to historique)"""
        return self.change_statut(locataire_id, StatutLocataire.HISTORIQUE)
    
    def reactiver(self, locataire_id: int) -> Optional[Locataire]:
        """Reactivate a Locataire"""
        return self.change_statut(locataire_id, StatutLocataire.ACTIF)
