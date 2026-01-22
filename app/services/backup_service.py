"""Backup service for database backup operations"""
import json
import os
import logging
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from app.utils.config import Config
from app.services.data_service import DataService
from app.services.google_drive_service import GoogleDriveService

logger = logging.getLogger(__name__)


class BackupService:
    BACKUP_FOLDER_NAME = "Gestion Locative Pro Backups"

    def __init__(self):
        self.config = Config.get_instance()
        self.data_service = DataService()
        self.google_drive = GoogleDriveService()
        self.backup_folder_id = None

    def _get_backup_folder_id(self) -> Optional[str]:
        """Get or create the backup folder ID"""
        if self.backup_folder_id:
            return self.backup_folder_id

        folder = self.google_drive.find_folder(self.BACKUP_FOLDER_NAME)
        if folder:
            self.backup_folder_id = folder['id']
            return self.backup_folder_id

        try:
            new_folder = self.google_drive.create_folder(self.BACKUP_FOLDER_NAME)
            self.backup_folder_id = new_folder['id']
            return self.backup_folder_id
        except Exception as e:
            logger.error(f"Failed to create backup folder: {e}")
            # Return None and let the main backup method handle the error
            return None

    def _generate_backup_filename(self) -> str:
        """Generate a unique backup filename with timestamp"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"gestion_locative_backup_{timestamp}.json"

    def _generate_temp_file_path(self, filename: str) -> str:
        """Generate a temporary file path for backup"""
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, filename)

    def backup_to_google_drive(self, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> Dict[str, Any]:
        """Export database and upload to Google Drive"""
        try:
            logger.info("Starting Google Drive backup...")

            data = self.data_service.export_all()
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            filename = self._generate_backup_filename()
            temp_file_path = self._generate_temp_file_path(filename)

            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(json_content)

            # Authenticate using saved token first, then with provided credentials if needed
            if client_id and client_secret:
                if not self.google_drive.authenticate_with_credentials(client_id, client_secret):
                    os.remove(temp_file_path)
                    raise Exception("Failed to authenticate with Google Drive")
            else:
                if not self.google_drive.authenticate():
                    os.remove(temp_file_path)
                    raise Exception("Failed to authenticate with Google Drive. Please provide credentials or authenticate first.")

            folder_id = self._get_backup_folder_id()
            result = self.google_drive.upload_content(
                content=json_content,
                file_name=filename,
                folder_id=folder_id
            )

            os.remove(temp_file_path)

            logger.info(f"Backup completed successfully: {result['id']}")
            return {
                'success': True,
                'file_id': result['id'],
                'file_name': result['name'],
                'web_link': result.get('web_view_link'),
                'created_time': result.get('created_time'),
                'backup_date': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            error_msg = str(e)
            
            # Check for common Google API errors and provide helpful messages
            if 'accessNotConfigured' in error_msg or 'Google Drive API has not been used' in error_msg:
                error_msg = (
                    "L'API Google Drive n'est pas activée pour ce projet.\n\n"
                    "Pour résoudre ce problème:\n"
                    "1. Allez sur https://console.cloud.google.com\n"
                    "2. Sélectionnez le projet avec l'ID: 837035454883\n"
                    "3. Naviguez vers APIs & Services → Bibliothèque\n"
                    "4. Recherchez 'Google Drive API' et activez-le\n"
                    "5. Attendez quelques minutes et réessayez\n\n"
                    f"Détails: {error_msg}"
                )
            elif 'media_filename' in error_msg:
                error_msg = (
                    "Erreur lors de l'envoi du fichier vers Google Drive.\n\n"
                    "Cela peut être dû à un problème de format de fichier.\n"
                    f"Détails: {error_msg}"
                )
            
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return {
                'success': False,
                'error': error_msg
            }

    def backup_to_local(self) -> Dict[str, Any]:
        """Export database and save to local backup directory"""
        try:
            logger.info("Starting local backup...")

            backup_dir = self.config.backup_directory
            if not backup_dir:
                backup_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'backups'))

            Path(backup_dir).mkdir(parents=True, exist_ok=True)

            data = self.data_service.export_all()
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"gestion_locative_backup_{timestamp}.json"
            file_path = os.path.join(backup_dir, filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            file_size = os.path.getsize(file_path)
            logger.info(f"Local backup completed: {file_path}")

            return {
                'success': True,
                'file_path': file_path,
                'file_name': filename,
                'file_size': file_size,
                'backup_date': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Local backup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def list_google_drive_backups(self) -> List[Dict[str, Any]]:
        """List all backups in Google Drive"""
        try:
            if not self.google_drive.is_authenticated():
                return []

            folder_id = self._get_backup_folder_id()
            files = self.google_drive.list_files(folder_id=folder_id)

            backups = []
            for f in files:
                backups.append({
                    'id': f['id'],
                    'name': f['name'],
                    'web_link': f.get('webViewLink'),
                    'created_time': f.get('createdTime'),
                    'modified_time': f.get('modifiedTime')
                })

            backups.sort(key=lambda x: x.get('created_time', ''), reverse=True)
            return backups

        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

    def restore_from_google_drive(self, file_id: str) -> Tuple[bool, str]:
        """Restore database from a Google Drive backup"""
        try:
            logger.info(f"Restoring from Google Drive backup: {file_id}")

            content = self.google_drive.get_file_content(file_id)
            data = json.loads(content)

            self.data_service.import_all(data)

            logger.info("Restore completed successfully")
            return True, "Database restored successfully from Google Drive"

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False, f"Restore failed: {str(e)}"

    def restore_from_local(self, file_path: str) -> Tuple[bool, str]:
        """Restore database from a local backup file"""
        try:
            logger.info(f"Restoring from local backup: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.data_service.import_all(data)

            logger.info("Restore completed successfully")
            return True, "Database restored successfully from local file"

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False, f"Restore failed: {str(e)}"

    def is_authenticated(self) -> bool:
        """Check if authenticated with Google Drive"""
        return self.google_drive.is_authenticated()

    def authenticate(self) -> bool:
        """Authenticate with Google Drive"""
        return self.google_drive.authenticate()
