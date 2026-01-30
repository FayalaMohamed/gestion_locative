"""Document management service for file operations"""
import os
import shutil
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from app.utils.config import Config
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for managing documents and folder structures"""

    ENTITY_TYPES = ["immeuble", "bureau", "locataire", "contrat", "paiement"]

    def __init__(self, session):
        self.session = session
        self.config = Config.get_instance()
        self.repo = DocumentRepository(session)
        self.documents_base_path = self._get_documents_base_path()

    def _get_documents_base_path(self) -> Path:
        base_path = Path.cwd() / "data" / "documents"
        base_path.mkdir(parents=True, exist_ok=True)
        return base_path

    def get_entity_base_path(self, entity_type: str) -> Path:
        entity_path = self.documents_base_path / entity_type
        entity_path.mkdir(parents=True, exist_ok=True)
        return entity_path

    def get_entity_item_path(self, entity_type: str, entity_id: int) -> Path:
        item_path = self.get_entity_base_path(entity_type) / str(entity_id)
        item_path.mkdir(parents=True, exist_ok=True)
        return item_path

    def get_full_folder_path(self, entity_type: str, entity_id: int, folder_path: str) -> Path:
        item_path = self.get_entity_item_path(entity_type, entity_id)
        full_path = item_path / folder_path if folder_path else item_path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path

    def get_tree_config(self, entity_type: str) -> Dict[str, Any]:
        config = self.repo.get_tree_config(entity_type)
        if config:
            return config.tree_structure
        return self.repo.get_default_tree_structure(entity_type)

    def save_tree_config(self, entity_type: str, tree_structure: Dict[str, Any]) -> None:
        self.repo.create_tree_config(entity_type, tree_structure)
        self.session.commit()

    def flatten_tree_paths(self, tree: Dict[str, Any], prefix: str = "") -> List[Tuple[str, str]]:
        """Convert tree structure to list of (display_path, storage_path) tuples"""
        paths = []
        name = tree.get("name", "")
        if prefix:
            display_path = f"{prefix}/{name}"
        else:
            display_path = name
        storage_path = prefix
        paths.append((display_path, storage_path))
        for child in tree.get("children", []):
            paths.extend(self.flatten_tree_paths(child, display_path))
        return paths

    def upload_file(
        self,
        entity_type: str,
        entity_id: int,
        folder_path: str,
        source_path: str,
        description: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Upload a file to the document storage"""
        try:
            source = Path(source_path)
            if not source.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")

            dest_folder = self.get_full_folder_path(entity_type, entity_id, folder_path)
            original_filename = source.name
            dest_path = dest_folder / original_filename

            # Handle filename conflicts by appending a number if file already exists
            counter = 1
            while dest_path.exists():
                name_stem = source.stem
                file_ext = source.suffix
                new_filename = f"{name_stem}_{counter}{file_ext}"
                dest_path = dest_folder / new_filename
                counter += 1

            shutil.copy2(source, dest_path)
            file_size = dest_path.stat().st_size

            doc = self.repo.create_document(
                entity_type=entity_type,
                entity_id=entity_id,
                folder_path=folder_path,
                filename=dest_path.name,
                original_name=source.name,
                file_type=self._get_file_type(source.suffix),
                file_size=file_size,
                description=description
            )

            return {
                "id": doc.id,
                "original_name": doc.original_name,
                "filename": doc.filename,
                "folder_path": doc.folder_path,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "created_at": doc.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def upload_files(
        self,
        entity_type: str,
        entity_id: int,
        folder_path: str,
        source_paths: List[str],
        descriptions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Upload multiple files"""
        results = []
        descs = descriptions or [None] * len(source_paths)
        for source_path, desc in zip(source_paths, descs):
            result = self.upload_file(entity_type, entity_id, folder_path, source_path, desc)
            if result:
                results.append(result)
        self.session.commit()
        return results

    def get_file_path(self, doc_id: int) -> Optional[Path]:
        """Get the full file path for a document"""
        doc = self.repo.get_document_by_id(doc_id)
        if doc:
            return self.get_entity_item_path(doc.entity_type, doc.entity_id) / doc.folder_path / doc.filename
        return None

    def delete_file(self, doc_id: int) -> bool:
        """Delete a document and its file"""
        try:
            doc = self.repo.get_document_by_id(doc_id)
            if not doc:
                return False

            file_path = self.get_file_path(doc_id)
            if file_path and file_path.exists():
                file_path.unlink()

            result = self.repo.delete_document(doc_id)
            if result:
                self.session.commit()
            return result
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def move_file(self, doc_id: int, new_folder_path: str) -> Optional[Dict[str, Any]]:
        """Move a document to a different folder"""
        try:
            doc = self.repo.get_document_by_id(doc_id)
            if not doc:
                return None

            old_path = self.get_file_path(doc_id)
            new_folder = self.get_full_folder_path(doc.entity_type, doc.entity_id, new_folder_path)
            new_path = new_folder / doc.filename

            if old_path and old_path.exists():
                shutil.move(str(old_path), str(new_path))

            doc = self.repo.update_document(doc_id, folder_path=new_folder_path)
            self.session.commit()
            return {
                "id": doc.id,
                "folder_path": doc.folder_path,
                "filename": doc.filename
            }
        except Exception as e:
            logger.error(f"Failed to move file: {e}")
            return None

    def update_document(self, doc_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update document metadata (e.g., original_name)"""
        try:
            doc = self.repo.update_document(doc_id, **kwargs)
            if doc:
                self.session.commit()
                return {
                    "id": doc.id,
                    "original_name": doc.original_name,
                    "filename": doc.filename,
                    "folder_path": doc.folder_path
                }
            return None
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return None

    def rename_document(self, doc_id: int, new_name: str) -> Optional[Dict[str, Any]]:
        """Rename a document and update both filename and original_name"""
        try:
            doc = self.repo.get_document_by_id(doc_id)
            if not doc:
                return None

            old_path = self.get_file_path(doc_id)
            if not old_path or not old_path.exists():
                raise FileNotFoundError(f"Document file not found: {old_path}")

            new_path = old_path.parent / new_name
            
            # Handle filename conflicts
            counter = 1
            while new_path.exists():
                name_stem = Path(new_name).stem
                file_ext = Path(new_name).suffix
                new_filename = f"{name_stem}_{counter}{file_ext}"
                new_path = old_path.parent / new_filename
                counter += 1

            # Rename the file
            shutil.move(str(old_path), str(new_path))

            # Update the document record
            doc = self.repo.update_document(
                doc_id,
                filename=new_path.name,
                original_name=new_name
            )
            self.session.commit()

            return {
                "id": doc.id,
                "original_name": doc.original_name,
                "filename": doc.filename,
                "folder_path": doc.folder_path
            }
        except Exception as e:
            logger.error(f"Failed to rename document: {e}")
            return None

    def get_documents_for_entity(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """Get all documents for an entity with file info"""
        docs = self.repo.get_documents_for_entity(entity_type, entity_id)
        return [
            {
                "id": doc.id,
                "folder_path": doc.folder_path,
                "original_name": doc.original_name,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "description": doc.description,
                "created_at": doc.created_at.isoformat()
            }
            for doc in docs
        ]

    def get_documents_by_folder(self, entity_type: str, entity_id: int, folder_path: str) -> List[Dict[str, Any]]:
        """Get documents in a specific folder"""
        docs = self.repo.get_documents_by_folder(entity_type, entity_id, folder_path)
        return [
            {
                "id": doc.id,
                "original_name": doc.original_name,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "description": doc.description,
                "created_at": doc.created_at.isoformat()
            }
            for doc in docs
        ]

    def search_documents(self, entity_type: str, entity_id: int, search_term: str) -> List[Dict[str, Any]]:
        """Search documents by name or description"""
        docs = self.repo.search_documents(entity_type, entity_id, search_term)
        return [
            {
                "id": doc.id,
                "folder_path": doc.folder_path,
                "original_name": doc.original_name,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "description": doc.description,
                "created_at": doc.created_at.isoformat()
            }
            for doc in docs
        ]

    def get_folder_contents(self, entity_type: str, entity_id: int, folder_path: str) -> Dict[str, Any]:
        """Get folder contents with subfolders and files"""
        item_path = self.get_entity_item_path(entity_type, entity_id)
        folder = item_path / folder_path if folder_path else item_path

        contents = {
            "folder_path": folder_path,
            "subfolders": [],
            "files": []
        }

        if folder.exists():
            for item in sorted(folder.iterdir()):
                if item.is_dir():
                    contents["subfolders"].append({
                        "name": item.name,
                        "path": str(item.relative_to(item_path))
                    })
                elif item.is_file():
                    doc = self._find_document_by_filename(entity_type, entity_id, folder_path, item.name)
                    contents["files"].append({
                        "name": item.name,
                        "display_name": doc.original_name if doc else item.name,
                        "size": item.stat().st_size,
                        "doc_id": doc.id if doc else None
                    })

        return contents

    def _find_document_by_filename(self, entity_type: str, entity_id: int, folder_path: str, filename: str):
        docs = self.repo.get_documents_by_folder(entity_type, entity_id, folder_path)
        for doc in docs:
            if doc.filename == filename:
                return doc
        return None

    def _get_file_type(self, suffix: str) -> str:
        """Get file type category from suffix"""
        suffix = suffix.lower()
        image_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
        document_types = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
        archive_types = ['.zip', '.rar', '.7z', '.tar', '.gz']

        if suffix in image_types:
            return "image"
        elif suffix in document_types:
            return "document"
        elif suffix in archive_types:
            return "archive"
        else:
            return "other"

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
