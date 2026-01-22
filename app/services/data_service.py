"""Data export/import service for JSON backup and restore"""
import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session

from app.database.connection import get_database
from app.models.entities import (
    Immeuble, Bureau, Locataire, Contrat, Paiement,
    TypePaiement, StatutLocataire, DocumentTreeConfig, Document
)


class DataService:
    def __init__(self, db: Optional[Session] = None, documents_base_path: Optional[str] = None):
        self.db = db
        self.documents_base_path = documents_base_path or str(Path.cwd() / "data" / "documents")

    def _get_session(self) -> Session:
        if self.db is None:
            db = get_database()
            return db.session_factory()
        return self.db

    def export_all(self, backup_folder: Optional[str] = None) -> Dict[str, Any]:
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
            data["entities"]["document_tree_configs"] = self._export_document_tree_configs(session)

            documents_info = self._export_documents(session)
            data["entities"]["documents"] = documents_info["metadata"]

            if backup_folder and documents_info["files"]:
                documents_backup_folder = os.path.join(backup_folder, "documents")
                os.makedirs(documents_backup_folder, exist_ok=True)
                for src, dst_rel in documents_info["files"]:
                    try:
                        dst = os.path.join(documents_backup_folder, dst_rel)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                    except Exception as e:
                        print(f"Warning: Could not copy document file {src}: {e}")

            return data
        finally:
            if self.db is None:
                session.close()

    def _export_documents(self, session: Session) -> Dict[str, Any]:
        """Export documents metadata and return file copy list"""
        documents = session.query(Document).all()
        files = []
        
        for doc in documents:
            src_path = self._get_document_file_path(doc.entity_type, doc.entity_id, doc.folder_path, doc.filename)
            if os.path.exists(src_path):
                dst_rel_path = os.path.join(doc.entity_type, str(doc.entity_id), doc.folder_path if doc.folder_path else "", doc.filename)
                files.append((src_path, dst_rel_path))
        
        metadata = [{
            "id": doc.id,
            "entity_type": doc.entity_type,
            "entity_id": doc.entity_id,
            "folder_path": doc.folder_path,
            "filename": doc.filename,
            "original_name": doc.original_name,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "description": doc.description,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
        } for doc in documents]
        
        return {"metadata": metadata, "files": files}

    def _get_document_file_path(self, entity_type: str, entity_id: int, folder_path: str, filename: str) -> str:
        if folder_path:
            return os.path.join(self.documents_base_path, entity_type, str(entity_id), folder_path, filename)
        return os.path.join(self.documents_base_path, entity_type, str(entity_id), filename)

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

    def _export_document_tree_configs(self, session: Session) -> List[Dict[str, Any]]:
        configs = session.query(DocumentTreeConfig).all()
        return [{
            "id": config.id,
            "entity_type": config.entity_type,
            "tree_structure": config.tree_structure,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        } for config in configs]

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

    def import_all(self, data: Dict[str, Any], documents_backup_folder: Optional[str] = None):
        """Import all data from a JSON dictionary"""
        session = self._get_session()

        try:
            entities = data.get("entities", {})

            self._import_immeubles(session, entities.get("immeubles", []))
            self._import_bureaux(session, entities.get("bureaux", []))
            self._import_locataires(session, entities.get("locataires", []))
            self._import_contrats(session, entities.get("contrats", []))
            self._import_paiements(session, entities.get("paiements", []))
            self._import_document_tree_configs(session, entities.get("document_tree_configs", []))
            self._import_documents(session, entities.get("documents", []))

            if documents_backup_folder and os.path.exists(documents_backup_folder):
                self._restore_document_files(documents_backup_folder)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if self.db is None:
                session.close()

    def _import_document_tree_configs(self, session: Session, items: List[Dict[str, Any]]):
        for item in items:
            existing = session.query(DocumentTreeConfig).filter(
                DocumentTreeConfig.entity_type == item["entity_type"]
            ).first()
            if existing:
                existing.tree_structure = item.get("tree_structure", {"name": item["entity_type"], "children": []})
                session.merge(existing)
            else:
                config = DocumentTreeConfig(
                    entity_type=item["entity_type"],
                    tree_structure=item.get("tree_structure", {"name": item["entity_type"], "children": []})
                )
                session.merge(config)

    def _import_documents(self, session: Session, items: List[Dict[str, Any]]):
        for item in items:
            doc = Document(
                id=item["id"],
                entity_type=item["entity_type"],
                entity_id=item["entity_id"],
                folder_path=item.get("folder_path", ""),
                filename=item["filename"],
                original_name=item["original_name"],
                file_type=item.get("file_type"),
                file_size=item.get("file_size"),
                description=item.get("description")
            )
            session.merge(doc)

    def _restore_document_files(self, documents_backup_folder: str):
        """Restore document files from backup folder"""
        for root, dirs, files in os.walk(documents_backup_folder):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, documents_backup_folder)
                dst_path = os.path.join(self.documents_base_path, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)

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
