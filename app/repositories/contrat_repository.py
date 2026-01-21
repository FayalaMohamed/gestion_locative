"""Contrat repository with business validation"""
from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.entities import Contrat
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
            Contrat.est_resilie_col == False
        ).all()
    
    def get_resilies(self) -> List[Contrat]:
        """Get all terminated contrats"""
        return self.session.query(Contrat).filter(
            Contrat.est_resilie_col == True
        ).all()
    
    def get_by_locataire(self, Locataire_id: int) -> List[Contrat]:
        """Get all contrats for a Locataire"""
        return self.filter_by(Locataire_id=Locataire_id)
    
    def get_actifs_by_locataire(self, Locataire_id: int) -> List[Contrat]:
        """Get active contrats for a Locataire"""
        return self.session.query(Contrat).filter(
            Contrat.Locataire_id == Locataire_id,
            Contrat.est_resilie_col == False
        ).all()
    
    def get_by_bureau(self, bureau_id: int) -> List[Contrat]:
        """Get contrats that include a specific bureau"""
        from app.models.entities import contrat_bureau
        return self.session.query(Contrat).join(
            contrat_bureau
        ).filter(
            contrat_bureau.c.bureau_id == bureau_id
        ).all()
    
    def get_contrat_actif_for_bureau(self, bureau_id: int) -> Optional[Contrat]:
        """Get the active contrat for a bureau (if any)"""
        from app.models.entities import contrat_bureau
        return self.session.query(Contrat).join(
            contrat_bureau
        ).filter(
            contrat_bureau.c.bureau_id == bureau_id,
            Contrat.est_resilie_col == False
        ).first()
    
    def create_with_validation(self, Locataire_id: int, date_debut: date, 
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
        
        # Validate date_debut is not in the future
        if date_debut > date.today():
            warnings.append(f"La date de début ({date_debut}) est dans le futur")
        
        # Check for overlapping contrats with same Locataire
        active_contrats = self.get_actifs_by_locataire(Locataire_id)
        if active_contrats:
            # Check date overlap
            for contrat in active_contrats:
                if contrat.date_fin is None or contrat.date_fin >= date_debut:
                    raise ContratValidationError(
                        f"Le locataire a déjà un contrat actif #{contrat.id} "
                        f"du {contrat.date_debut} sans date de fin définie"
                    )
                if contrat.date_fin >= date_debut:
                    raise ContratValidationError(
                        f"Le locataire a un contrat actif #{contrat.id} "
                        f"jusqu'au {contrat.date_fin}"
                    )
        
        # Validate bureaux
        if bureaux is None:
            bureaux = []
        
        # Check if bureaux are available
        from app.models.entities import Bureau
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
        
        # Create the contrat
        contrat = Contrat(
            Locataire_id=Locataire_id,
            date_debut=date_debut,
            montant_mensuel=montant_mensuel,
            **kwargs
        )
        
        # Add bureaux
        if bureaux:
            contrat.bureaux = bureaux
        
        self.session.add(contrat)
        self.session.flush()
        
        return contrat, warnings
    
    def resilier(self, contrat_id: int, date_resiliation: date, 
                 motif: str = None) -> Optional[Contrat]:
        """Terminate a contrat"""
        contrat = self.get_by_id(contrat_id)
        if contrat:
            contrat.est_resilie_col = True
            contrat.date_resiliation = date_resiliation
            contrat.motif_resiliation = motif
            self.session.flush()
        return contrat
    
    def reactiver(self, contrat_id: int, nouvelle_date_debut: date = None) -> Optional[Contrat]:
        """Reactivate a terminated contrat"""
        contrat = self.get_by_id(contrat_id)
        if contrat:
            contrat.est_resilie_col = False
            contrat.date_resiliation = None
            contrat.motif_resiliation = None
            if nouvelle_date_debut:
                contrat.date_debut = nouvelle_date_debut
            self.session.flush()
        return contrat
    
    def ajouter_bureau(self, contrat_id: int, bureau) -> Optional[Contrat]:
        """Add a bureau to an existing contrat"""
        contrat = self.get_by_id(contrat_id)
        if contrat:
            # Check if bureau is available
            existing = self.get_contrat_actif_for_bureau(bureau.id)
            if existing and existing.id != contrat_id:
                raise ContratValidationError(
                    f"Le bureau {bureau.numero} est déjà utilisé par le contrat #{existing.id}"
                )
            
            if bureau not in contrat.bureaux:
                contrat.bureaux.append(bureau)
                self.session.flush()
        return contrat
    
    def retirer_bureau(self, contrat_id: int, bureau) -> Optional[Contrat]:
        """Remove a bureau from an existing contrat"""
        contrat = self.get_by_id(contrat_id)
        if contrat and bureau in contrat.bureaux:
            contrat.bureaux.remove(bureau)
            self.session.flush()
        return contrat
    
    def get_contrats_par_annee(self, annee: int) -> List[Contrat]:
        """Get all contrats that were active during a given year"""
        start_of_year = date(annee, 1, 1)
        end_of_year = date(annee, 12, 31)
        
        return self.session.query(Contrat).filter(
            Contrat.date_debut <= end_of_year,
            (Contrat.date_fin.is_(None)) | (Contrat.date_fin >= start_of_year)
        ).all()
    
    def search(self, query: str) -> List[Contrat]:
        """Search contrats by Locataire name or bureau numero"""
        search_term = f"%{query}%"
        from app.models.entities import Locataire
        return self.session.query(Contrat).join(Locataire).filter(
            (Locataire.nom.ilike(search_term)) |
            (Locataire.raison_sociale.ilike(search_term))
        ).all()
