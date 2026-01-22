from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.entities import Document, DocumentTreeConfig
from app.repositories.base import BaseRepository


class DocumentRepository:
    """Repository for document-related database operations"""

    def __init__(self, session: Session):
        self.session = session

    # Document operations
    def get_document_by_id(self, id: int) -> Optional[Document]:
        return self.session.query(Document).filter(Document.id == id).first()

    def get_documents_for_entity(self, entity_type: str, entity_id: int) -> List[Document]:
        return self.session.query(Document).filter(
            Document.entity_type == entity_type,
            Document.entity_id == entity_id
        ).all()

    def get_documents_by_folder(self, entity_type: str, entity_id: int, folder_path: str) -> List[Document]:
        return self.session.query(Document).filter(
            Document.entity_type == entity_type,
            Document.entity_id == entity_id,
            Document.folder_path == folder_path
        ).all()

    def create_document(
        self,
        entity_type: str,
        entity_id: int,
        folder_path: str,
        filename: str,
        original_name: str,
        file_type: Optional[str] = None,
        file_size: Optional[int] = None,
        description: Optional[str] = None
    ) -> Document:
        doc = Document(
            entity_type=entity_type,
            entity_id=entity_id,
            folder_path=folder_path,
            filename=filename,
            original_name=original_name,
            file_type=file_type,
            file_size=file_size,
            description=description
        )
        self.session.add(doc)
        self.session.flush()
        return doc

    def update_document(self, doc_id: int, **kwargs) -> Optional[Document]:
        doc = self.get_document_by_id(doc_id)
        if doc:
            for key, value in kwargs.items():
                if hasattr(doc, key):
                    setattr(doc, key, value)
            self.session.flush()
        return doc

    def delete_document(self, doc_id: int) -> bool:
        doc = self.get_document_by_id(doc_id)
        if doc:
            self.session.delete(doc)
            self.session.flush()
            return True
        return False

    def search_documents(self, entity_type: str, entity_id: int, search_term: str) -> List[Document]:
        search_pattern = f"%{search_term}%"
        return self.session.query(Document).filter(
            Document.entity_type == entity_type,
            Document.entity_id == entity_id,
            (Document.original_name.like(search_pattern) |
             Document.filename.like(search_pattern) |
             Document.description.like(search_pattern))
        ).all()

    # Tree config operations
    def get_tree_config(self, entity_type: str) -> Optional[DocumentTreeConfig]:
        return self.session.query(DocumentTreeConfig).filter(
            DocumentTreeConfig.entity_type == entity_type
        ).first()

    def get_all_tree_configs(self) -> List[DocumentTreeConfig]:
        return self.session.query(DocumentTreeConfig).all()

    def create_tree_config(self, entity_type: str, tree_structure: Dict[str, Any]) -> DocumentTreeConfig:
        existing = self.get_tree_config(entity_type)
        if existing:
            from sqlalchemy import update
            self.session.execute(
                update(DocumentTreeConfig)
                .where(DocumentTreeConfig.entity_type == entity_type)
                .values(tree_structure=tree_structure)
            )
            self.session.flush()
            config = self.get_tree_config(entity_type)
            if config:
                return config
            raise Exception("Failed to retrieve updated config")
        config = DocumentTreeConfig(
            entity_type=entity_type,
            tree_structure=tree_structure
        )
        self.session.add(config)
        self.session.flush()
        return config

    def delete_tree_config(self, entity_type: str) -> bool:
        config = self.get_tree_config(entity_type)
        if config:
            self.session.delete(config)
            self.session.flush()
            return True
        return False

    def get_default_tree_structure(self, entity_type: str) -> Dict[str, Any]:
        defaults = {
            "immeuble": {
                "name": "Immeuble",
                "children": [
                    {"name": "Documents Légaux", "children": []},
                    {"name": "Photos", "children": []},
                    {"name": "Plans", "children": []}
                ]
            },
            "bureau": {
                "name": "Bureau",
                "children": [
                    {"name": "Photos", "children": [
                        {"name": "Extérieur", "children": []},
                        {"name": "Intérieur", "children": []}
                    ]},
                    {"name": "Plans", "children": []},
                    {"name": "Équipements", "children": []}
                ]
            },
            "locataire": {
                "name": "Locataire",
                "children": [
                    {"name": "Pièce d'identité", "children": []},
                    {"name": "Documents Bancaires", "children": []},
                    {"name": "Assurance", "children": []}
                ]
            },
            "contrat": {
                "name": "Contrat",
                "children": [
                    {"name": "Contrat Signé", "children": []},
                    {"name": "Annexes", "children": []},
                    {"name": "Avenants", "children": []}
                ]
            },
            "paiement": {
                "name": "Paiement",
                "children": [
                    {"name": "Reçus", "children": []},
                    {"name": "Justificatifs", "children": []}
                ]
            }
        }
        return defaults.get(entity_type, {"name": entity_type, "children": []})
