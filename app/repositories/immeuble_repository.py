"""Immeuble repository"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.entities import Immeuble
from app.repositories.base import BaseRepository


class ImmeubleRepository(BaseRepository[Immeuble]):
    """Repository for Immeuble CRUD operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Immeuble)
    
    def get_by_nom(self, nom: str) -> Optional[Immeuble]:
        """Find immeuble by name"""
        return self.first(nom=nom)
    
    def get_disponibles(self) -> List[Immeuble]:
        """Get all immeubles (no specific availability filter)"""
        return self.get_all()
    
    def search(self, query: str) -> List[Immeuble]:
        """Search immeubles by name or address"""
        return self.session.query(Immeuble).filter(
            (Immeuble.nom.ilike(f"%{query}%")) |
            (Immeuble.adresse.ilike(f"%{query}%"))
        ).all()
    
    def get_with_bureaux_count(self) -> List[Immeuble]:
        """Get all immeubles with their bureaux count"""
        from sqlalchemy import func
        return self.session.query(
            Immeuble,
            func.count(Immeuble.bureaux).label('bureaux_count')
        ).outerjoin(Immeuble.bureaux).group_by(Immeuble.id).all()
