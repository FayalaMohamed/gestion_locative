"""Contrat repository with business validation"""
from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy.orm import Session

from app.models.entities import Contrat, contrat_bureau, Bureau, Locataire, StatutLocataire
from app.repositories.base import BaseRepository


class ContratValidationError(Exception):
    """Exception raised when contrat validation fails"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ContratRepository(BaseRepository[Contrat]):
    """Repository for Contrat CRUD operations with business validation"""
    
    def __init__(self, session: Session):
        super().__init__(session, Contrat)
    
    def get_actifs(self) -> List[Contrat]:
        """Get all active contrats"""
        return self.session.query(Contrat).filter(
            Contrat.est_resilie == False
        ).all()
    
    def get_resilies(self) -> List[Contrat]:
        """Get all terminated contrats"""
        return self.session.query(Contrat).filter(
            Contrat.est_resilie == True
        ).all()
    
    def get_by_locataire(self, locataire_id: int) -> List[Contrat]:
        """Get all contrats for a Locataire"""
        return self.filter_by(locataire_id=locataire_id)
    
    def get_actifs_by_locataire(self, locataire_id: int) -> List[Contrat]:
        """Get active contrats for a Locataire"""
        return self.session.query(Contrat).filter(
            Contrat.locataire_id == locataire_id,
            Contrat.est_resilie == False
        ).all()
    
    def get_by_bureau(self, bureau_id: int) -> List[Contrat]:
        """Get contrats that include a specific bureau"""
        return self.session.query(Contrat).join(
            contrat_bureau
        ).filter(
            contrat_bureau.c.bureau_id == bureau_id
        ).all()
    
    def get_contrat_actif_for_bureau(self, bureau_id: int) -> Optional[Contrat]:
        """Get the active contrat for a bureau (if any)"""
        return self.session.query(Contrat).join(
            contrat_bureau
        ).filter(
            contrat_bureau.c.bureau_id == bureau_id,
            Contrat.est_resilie == False
        ).first()
    
    def create_with_validation(self, locataire_id: int, date_debut: date, 
                                montant_mensuel: float, bureaux: list = None,
                                **kwargs) -> Tuple[Contrat, List[str]]:
        """
        Create a contrat with business validation.
        
        Returns:
            Tuple of (Contrat, list of warnings)
        
        Raises:
            ContratValidationError: If validation fails
        """
        warnings = []
        
        if date_debut > date.today():
            warnings.append(f"La date de début ({date_debut}) est dans le futur")
        
        active_contrats = self.get_actifs_by_locataire(locataire_id)
        if active_contrats:
            raise ContratValidationError(
                f"Le locataire a déjà un contrat actif #{active_contrats[0].id} "
                f"commencé le {active_contrats[0].date_debut}"
            )
        
        if bureaux is None:
            bureaux = []
        
        unavailable_bureaux = []
        for bureau in bureaux:
            existing = self.get_contrat_actif_for_bureau(bureau.id)
            if existing:
                unavailable_bureaux.append((bureau.numero, existing.id))
        
        if unavailable_bureaux:
            msg = ", ".join([f"{num} (contrat #{cid})" for num, cid in unavailable_bureaux])
            raise ContratValidationError(
                f"Les bureaux suivants sont déjà occupés: {msg}"
            )
        
        contrat = Contrat(
            locataire_id=locataire_id,
            date_debut=date_debut,
            montant_mensuel=montant_mensuel,
            **kwargs
        )
        
        if bureaux:
            contrat.bureaux = bureaux
            for bureau in bureaux:
                bureau.est_disponible = False
        
        self.session.add(contrat)
        self.session.flush()
        
        return contrat, warnings
    
    def resilier(self, contrat_id: int, date_resiliation: date,
                 motif: str = None) -> Optional[Contrat]:
        """Terminate a contrat"""
        contrat = self.get_by_id(contrat_id)
        if contrat:
            contrat.est_resilie = True
            contrat.date_resiliation = date_resiliation
            contrat.motif_resiliation = motif
            loc_id = contrat.locataire_id
            
            for bureau in contrat.bureaux:
                other_active = self.session.query(Contrat).join(
                    contrat_bureau, Contrat.id == contrat_bureau.c.contrat_id
                ).filter(
                    contrat_bureau.c.bureau_id == bureau.id,
                    Contrat.id != contrat_id,
                    Contrat.est_resilie == False
                ).first()
                
                if not other_active:
                    bureau.est_disponible = True
            
            self.session.flush()
            
            active_count = self.session.query(Contrat).filter(
                Contrat.locataire_id == loc_id,
                Contrat.est_resilie == False
            ).count()
            
            if active_count == 0:
                locataire = self.session.query(Locataire).get(loc_id)
                if locataire:
                    locataire.statut = StatutLocataire.HISTORIQUE
                    self.session.flush()
                    
        return contrat
    
    def reactiver(self, contrat_id: int, nouvelle_date_debut: date = None) -> Optional[Contrat]:
        """Reactivate a terminated contrat"""
        contrat = self.get_by_id(contrat_id)
        if contrat:
            contrat.est_resilie = False
            contrat.date_resiliation = None
            contrat.motif_resiliation = None
            if nouvelle_date_debut:
                contrat.date_debut = nouvelle_date_debut
            
            loc_id = contrat.locataire_id
            
            for bureau in contrat.bureaux:
                bureau.est_disponible = False
            
            self.session.flush()
            
            locataire = self.session.query(Locataire).get(loc_id)
            if locataire:
                locataire.statut = StatutLocataire.ACTIF
                self.session.flush()
                
        return contrat
    
    def ajouter_bureau(self, contrat_id: int, bureau) -> Optional[Contrat]:
        """Add a bureau to an existing contrat"""
        contrat = self.get_by_id(contrat_id)
        if contrat:
            existing = self.get_contrat_actif_for_bureau(bureau.id)
            if existing and existing.id != contrat_id:
                raise ContratValidationError(
                    f"Le bureau {bureau.numero} est déjà utilisé par le contrat #{existing.id}"
                )
            
            if bureau not in contrat.bureaux:
                contrat.bureaux.append(bureau)
                bureau.est_disponible = False
                self.session.flush()
        return contrat
    
    def retirer_bureau(self, contrat_id: int, bureau) -> Optional[Contrat]:
        """Remove a bureau from an existing contrat"""
        contrat = self.get_by_id(contrat_id)
        if contrat and bureau in contrat.bureaux:
            contrat.bureaux.remove(bureau)
            
            other_active = self.session.query(Contrat).join(
                Contrat.bureaux
            ).filter(
                Bureau.id == bureau.id,
                Contrat.id != contrat_id,
                Contrat.est_resilie == False
            ).first()
            
            if not other_active:
                bureau.est_disponible = True
            
            self.session.flush()
        return contrat
    
    def get_contrats_par_annee(self, annee: int) -> List[Contrat]:
        """Get all contrats that were active during a given year"""
        start_of_year = date(annee, 1, 1)
        end_of_year = date(annee, 12, 31)
        
        return self.session.query(Contrat).filter(
            Contrat.date_debut <= end_of_year,
            (Contrat.est_resilie == False) | 
            ((Contrat.est_resilie == True) & (Contrat.date_resiliation >= start_of_year))
        ).all()
    
    def search(self, query: str) -> List[Contrat]:
        """Search contrats by Locataire name or bureau numero"""
        search_term = f"%{query}%"
        return self.session.query(Contrat).join(Locataire).filter(
            (Locataire.nom.ilike(search_term)) |
            (Locataire.raison_sociale.ilike(search_term))
        ).all()
