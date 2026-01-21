"""Paiement repository"""
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.entities import Paiement, TypePaiement
from app.repositories.base import BaseRepository


class PaiementRepository(BaseRepository[Paiement]):
    """Repository for Paiement CRUD operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Paiement)
    
    def get_by_contrat(self, contrat_id: int) -> List[Paiement]:
        """Get all payments for a contrat"""
        return self.filter_by(contrat_id=contrat_id)
    
    def get_by_locataire(self, Locataire_id: int) -> List[Paiement]:
        """Get all payments for a Locataire"""
        return self.filter_by(Locataire_id=Locataire_id)
    
    def get_by_type(self, type_paiement: TypePaiement) -> List[Paiement]:
        """Get payments by type"""
        return self.filter_by(type_paiement=type_paiement)
    
    def get_by_periode(self, start_date: date, end_date: date) -> List[Paiement]:
        """Get payments within a date range"""
        return self.session.query(Paiement).filter(
            Paiement.date_paiement >= start_date,
            Paiement.date_paiement <= end_date
        ).all()
    
    def get_by_contrat_and_type(self, contrat_id: int, type_paiement: TypePaiement) -> List[Paiement]:
        """Get payments for a contrat by type"""
        return self.session.query(Paiement).filter(
            Paiement.contrat_id == contrat_id,
            Paiement.type_paiement == type_paiement
        ).all()
    
    def get_loyers_impayes(self, contrat_id: int, upto_date: date = None) -> List[tuple]:
        """
        Get unpaid months for a contrat.
        
        Returns:
            List of (year, month) tuples representing unpaid months
        """
        if upto_date is None:
            upto_date = date.today()
        
        # Get all contrat details
        from app.models.entities import Contrat
        contrat = self.session.query(Contrat).filter(Contrat.id == contrat_id).first()
        if not contrat:
            return []
        
        # Get all rent payments
        paiements_loyer = self.get_by_contrat_and_type(contrat_id, TypePaiement.LOYER)
        
        # Build set of covered months
        mois_couverts = set()
        for paiement in paiements_loyer:
            mois_couverts.update(paiement.get_mois_couverts())
        
        # Generate expected months
        mois_impayes = []
        current = contrat.date_debut
        
        while current <= upto_date:
            if current >= contrat.date_debut:
                if (current.year, current.month) not in mois_couverts:
                    mois_impayes.append((current.year, current.month))
            
            # Move to next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
        
        return mois_impayes
    
    def get_total_loyers_payes(self, contrat_id: int, year: int = None) -> Decimal:
        """Get total rent paid for a contrat (optionally for a specific year)"""
        from sqlalchemy import func
        
        query = self.session.query(
            func.coalesce(func.sum(Paiement.montant_total), 0)
        ).filter(
            Paiement.contrat_id == contrat_id,
            Paiement.type_paiement == TypePaiement.LOYER
        )
        
        if year:
            start = date(year, 1, 1)
            end = date(year, 12, 31)
            query = query.filter(
                Paiement.date_paiement >= start,
                Paiement.date_paiement <= end
            )
        
        result = query.scalar()
        return result if result else Decimal("0")
    
    def create_paiement_loyer(self, Locataire_id: int, contrat_id: int,
                               montant_total: Decimal, date_paiement: date,
                               date_debut_periode: date, date_fin_periode: date,
                               commentaire: str = None) -> Paiement:
        """Create a rent payment"""
        return self.create(
            Locataire_id=Locataire_id,
            contrat_id=contrat_id,
            type_paiement=TypePaiement.LOYER,
            montant_total=montant_total,
            date_paiement=date_paiement,
            date_debut_periode=date_debut_periode,
            date_fin_periode=date_fin_periode,
            commentaire=commentaire
        )
    
    def create_paiement_autre(self, Locataire_id: int, contrat_id: int,
                               type_paiement: TypePaiement, montant_total: Decimal,
                               date_paiement: date, commentaire: str = None) -> Paiement:
        """Create a non-rent payment (caution, pas de porte, etc.)"""
        return self.create(
            Locataire_id=Locataire_id,
            contrat_id=contrat_id,
            type_paiement=type_paiement,
            montant_total=montant_total,
            date_paiement=date_paiement,
            commentaire=commentaire
        )
    
    def get_recents(self, jours: int = 30) -> List[Paiement]:
        """Get recent payments within N days"""
        from datetime import timedelta
        start_date = date.today() - timedelta(days=jours)
        return self.get_by_periode(start_date, date.today())
    
    def get_by_date(self, date_paiement: date) -> List[Paiement]:
        """Get all payments on a specific date"""
        return self.filter_by(date_paiement=date_paiement)
    
    def search(self, query: str) -> List[Paiement]:
        """Search payments by commentaire"""
        search_term = f"%{query}%"
        return self.session.query(Paiement).filter(
            Paiement.commentaire.ilike(search_term)
        ).all()
    
    def get_montant_total_by_type(self, type_paiement: TypePaiement,
                                   start_date: date = None,
                                   end_date: date = None) -> Decimal:
        """Get total amount for a payment type within date range"""
        from sqlalchemy import func
        
        query = self.session.query(
            func.coalesce(func.sum(Paiement.montant_total), 0)
        ).filter(
            Paiement.type_paiement == type_paiement
        )
        
        if start_date:
            query = query.filter(Paiement.date_paiement >= start_date)
        if end_date:
            query = query.filter(Paiement.date_paiement <= end_date)
        
        result = query.scalar()
        return result if result else Decimal("0")
