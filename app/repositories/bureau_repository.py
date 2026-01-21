"""Bureau repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.entities import Bureau
from app.repositories.base import BaseRepository


class BureauRepository(BaseRepository[Bureau]):
    """Repository for Bureau CRUD operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Bureau)
    
    def get_by_numero(self, immeuble_id: int, numero: str) -> Optional[Bureau]:
        """Find bureau by immeuble and numero"""
        return self.first(immeuble_id=immeuble_id, numero=numero)
    
    def get_by_immeuble(self, immeuble_id: int) -> List[Bureau]:
        """Get all bureaux in an immeuble"""
        return self.filter_by(immeuble_id=immeuble_id)
    
    def get_disponibles(self, immeuble_id: Optional[int] = None) -> List[Bureau]:
        """Get available bureaux"""
        query = self.session.query(Bureau).filter(Bureau.est_disponible == True)
        if immeuble_id:
            query = query.filter(Bureau.immeuble_id == immeuble_id)
        return query.all()
    
    def get_occupes(self, immeuble_id: Optional[int] = None) -> List[Bureau]:
        """Get occupied bureaux"""
        query = self.session.query(Bureau).filter(Bureau.est_disponible == False)
        if immeuble_id:
            query = query.filter(Bureau.immeuble_id == immeuble_id)
        return query.all()
    
    def search(self, query: str) -> List[Bureau]:
        """Search bureaux by numero, etage or notes"""
        return self.session.query(Bureau).filter(
            (Bureau.numero.ilike(f"%{query}%")) |
            (Bureau.etage.ilike(f"%{query}%")) |
            (Bureau.notes.ilike(f"%{query}%"))
        ).all()
    
    def get_by_etage(self, etage: str) -> List[Bureau]:
        """Get bureaux by floor"""
        return self.filter_by(etage=etage)
    
    def get_by_surface_range(self, min_surface: float, max_surface: float) -> List[Bureau]:
        """Get bureaux within surface range"""
        return self.session.query(Bureau).filter(
            Bureau.surface_m2 >= min_surface,
            Bureau.surface_m2 <= max_surface
        ).all()
    
    def update_disponibilite(self, bureau_id: int, est_disponible: bool) -> Optional[Bureau]:
        """Update bureau availability"""
        bureau = self.get_by_id(bureau_id)
        if bureau:
            bureau.est_disponible = est_disponible
            self.session.flush()
        return bureau
