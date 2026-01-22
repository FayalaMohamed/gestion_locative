"""Data export/import service for JSON backup and restore"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.database.connection import get_database
from app.models.entities import (
    Immeuble, Bureau, Locataire, Contrat, Paiement,
    TypePaiement, StatutLocataire
)


class DataService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def _get_session(self) -> Session:
        if self.db is None:
            db = get_database()
            return db.session_factory()
        return self.db

    def export_all(self) -> Dict[str, Any]:
        """Export all data to a JSON-compatible dictionary"""
        session = self._get_session()
        data = {
            "version": "1.0",
            "export_date": datetime.utcnow().isoformat(),
            "entities": {}
        }

        try:
            data["entities"]["immeubles"] = self._export_immeubles(session)
            data["entities"]["bureaux"] = self._export_bureaux(session)
            data["entities"]["locataires"] = self._export_locataires(session)
            data["entities"]["contrats"] = self._export_contrats(session)
            data["entities"]["paiements"] = self._export_paiements(session)

            return data
        finally:
            if self.db is None:
                session.close()

    def _export_immeubles(self, session: Session) -> List[Dict[str, Any]]:
        immeuble = session.query(Immeuble).all()
        return [self._serialize_immeuble(i) for i in immeuble]

    def _export_bureaux(self, session: Session) -> List[Dict[str, Any]]:
        bureaux = session.query(Bureau).all()
        return [self._serialize_bureau(b) for b in bureaux]

    def _export_locataires(self, session: Session) -> List[Dict[str, Any]]:
        locataires = session.query(Locataire).all()
        return [self._serialize_locataire(l) for l in locataires]

    def _export_contrats(self, session: Session) -> List[Dict[str, Any]]:
        contrats = session.query(Contrat).all()
        return [self._serialize_contrat(c) for c in contrats]

    def _export_paiements(self, session: Session) -> List[Dict[str, Any]]:
        paiements = session.query(Paiement).all()
        return [self._serialize_paiement(p) for p in paiements]

    def _serialize_immeuble(self, obj: Immeuble) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "nom": obj.nom,
            "adresse": obj.adresse,
            "notes": obj.notes,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
        }

    def _serialize_bureau(self, obj: Bureau) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "immeuble_id": obj.immeuble_id,
            "numero": obj.numero,
            "etage": obj.etage,
            "surface_m2": obj.surface_m2,
            "notes": obj.notes,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
        }

    def _serialize_locataire(self, obj: Locataire) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "nom": obj.nom,
            "telephone": obj.telephone,
            "email": obj.email,
            "cin": obj.cin,
            "raison_sociale": obj.raison_sociale,
            "statut": obj.statut.value if obj.statut else None,
            "commentaires": obj.commentaires,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
        }

    def _serialize_contrat(self, obj: Contrat) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "locataire_id": obj.Locataire_id,
            "bureau_ids": [b.id for b in obj.bureaux] if obj.bureaux else [],
            "date_debut": obj.date_debut.isoformat() if obj.date_debut else None,
            "date_derniere_augmentation": obj.date_derniere_augmentation.isoformat() if obj.date_derniere_augmentation else None,
            "montant_premier_mois": float(obj.montant_premier_mois) if obj.montant_premier_mois else None,
            "montant_mensuel": float(obj.montant_mensuel) if obj.montant_mensuel else None,
            "montant_caution": float(obj.montant_caution) if obj.montant_caution else None,
            "montant_pas_de_porte": float(obj.montant_pas_de_porte) if obj.montant_pas_de_porte else None,
            "compteur_steg": obj.compteur_steg,
            "compteur_sonede": obj.compteur_sonede,
            "est_resilie_col": obj.est_resilie_col,
            "date_resiliation": obj.date_resiliation.isoformat() if obj.date_resiliation else None,
            "motif_resiliation": obj.motif_resiliation,
            "conditions": obj.conditions,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
        }

    def _serialize_paiement(self, obj: Paiement) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "locataire_id": obj.Locataire_id,
            "contrat_id": obj.contrat_id,
            "type_paiement": obj.type_paiement.value if obj.type_paiement else None,
            "montant_total": float(obj.montant_total) if obj.montant_total else None,
            "date_paiement": obj.date_paiement.isoformat() if obj.date_paiement else None,
            "date_debut_periode": obj.date_debut_periode.isoformat() if obj.date_debut_periode else None,
            "date_fin_periode": obj.date_fin_periode.isoformat() if obj.date_fin_periode else None,
            "commentaire": obj.commentaire,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
        }

    def import_all(self, data: Dict[str, Any]):
        """Import all data from a JSON dictionary"""
        session = self._get_session()

        try:
            entities = data.get("entities", {})

            self._import_immeubles(session, entities.get("immeubles", []))
            self._import_bureaux(session, entities.get("bureaux", []))
            self._import_locataires(session, entities.get("locataires", []))
            self._import_contrats(session, entities.get("contrats", []))
            self._import_paiements(session, entities.get("paiements", []))

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if self.db is None:
                session.close()

    def _import_immeubles(self, session: Session, items: List[Dict[str, Any]]):
        for item in items:
            immeuble = Immeuble(
                id=item["id"],
                nom=item["nom"],
                adresse=item.get("adresse"),
                notes=item.get("notes")
            )
            session.merge(immeuble)

    def _import_bureaux(self, session: Session, items: List[Dict[str, Any]]):
        for item in items:
            bureau = Bureau(
                id=item["id"],
                immeuble_id=item["immeuble_id"],
                numero=item["numero"],
                etage=item.get("etage"),
                surface_m2=item.get("surface_m2"),
                notes=item.get("notes")
            )
            session.merge(bureau)

    def _import_locataires(self, session: Session, items: List[Dict[str, Any]]):
        for item in items:
            statut = StatutLocataire(item["statut"]) if item.get("statut") else StatutLocataire.ACTIF
            locataire = Locataire(
                id=item["id"],
                nom=item["nom"],
                telephone=item.get("telephone"),
                email=item.get("email"),
                cin=item.get("cin"),
                raison_sociale=item.get("raison_sociale"),
                statut=statut,
                commentaires=item.get("commentaires")
            )
            session.merge(locataire)

    def _import_contrats(self, session: Session, items: List[Dict[str, Any]]):
        from datetime import date
        for item in items:
            date_debut = date.fromisoformat(item["date_debut"]) if item.get("date_debut") else None
            date_derniere_augmentation = date.fromisoformat(item["date_derniere_augmentation"]) if item.get("date_derniere_augmentation") else None
            date_resiliation = date.fromisoformat(item["date_resiliation"]) if item.get("date_resiliation") else None

            contrat = Contrat(
                id=item["id"],
                Locataire_id=item["locataire_id"],
                date_debut=date_debut,
                date_derniere_augmentation=date_derniere_augmentation,
                montant_premier_mois=item.get("montant_premier_mois"),
                montant_mensuel=item.get("montant_mensuel"),
                montant_caution=item.get("montant_caution"),
                montant_pas_de_porte=item.get("montant_pas_de_porte"),
                compteur_steg=item.get("compteur_steg"),
                compteur_sonede=item.get("compteur_sonede"),
                est_resilie_col=item.get("est_resilie_col", False),
                date_resiliation=date_resiliation,
                motif_resiliation=item.get("motif_resiliation"),
                conditions=item.get("conditions")
            )
            session.merge(contrat)
        session.flush()

        for item in items:
            bureau_ids = item.get("bureau_ids", [])
            if bureau_ids:
                contrat = session.query(Contrat).get(item["id"])
                if contrat:
                    bureaux = session.query(Bureau).filter(Bureau.id.in_(bureau_ids)).all()
                    contrat.bureaux = bureaux
                    session.merge(contrat)

    def _import_paiements(self, session: Session, items: List[Dict[str, Any]]):
        from datetime import date
        for item in items:
            type_paiement = TypePaiement(item["type_paiement"]) if item.get("type_paiement") else TypePaiement.AUTRE
            date_paiement = date.fromisoformat(item["date_paiement"]) if item.get("date_paiement") else None
            date_debut_periode = date.fromisoformat(item["date_debut_periode"]) if item.get("date_debut_periode") else None
            date_fin_periode = date.fromisoformat(item["date_fin_periode"]) if item.get("date_fin_periode") else None

            paiement = Paiement(
                id=item["id"],
                Locataire_id=item["locataire_id"],
                contrat_id=item["contrat_id"],
                type_paiement=type_paiement,
                montant_total=item.get("montant_total"),
                date_paiement=date_paiement,
                date_debut_periode=date_debut_periode,
                date_fin_periode=date_fin_periode,
                commentaire=item.get("commentaire")
            )
            session.merge(paiement)
