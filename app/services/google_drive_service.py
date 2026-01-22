"""Google Drive service for backup operations"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from io import BytesIO

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

REDIRECT_URI = 'http://localhost:8080/callback'


class GoogleDriveService:
    def __init__(self):
        self.token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'google_drive_token.json')
        self._service = None
        self._creds = None

    def _get_default_credentials_path(self) -> Optional[str]:
        """Find credentials file in common locations"""
        search_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials', 'client_secret.json'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials', 'credentials.json'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client_secret.json'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json'),
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        return None

    def _load_credentials(self) -> Optional[Credentials]:
        """Load credentials from token file or return None"""
        if os.path.exists(self.token_path):
            try:
                self._creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                return self._creds
            except Exception as e:
                logger.warning(f"Failed to load token file: {e}")
                try:
                    os.remove(self.token_path)
                except:
                    pass
        return None

    def _save_credentials(self):
        """Save credentials to token file"""
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
        with open(self.token_path, 'w') as token:
            token.write(self._creds.to_json())
        print(f"DEBUG: Credentials saved to {self.token_path}")

    def authenticate_with_credentials(self, client_id: str, client_secret: str) -> bool:
        """Authenticate with Google Drive using provided OAuth credentials.
        Credentials are only used for initial authentication and then discarded from memory.
        Only the OAuth token is saved to disk.
        """
        # First, try to use existing saved token
        creds = self._load_credentials()

        if creds and creds.valid:
            self._creds = creds
            return True

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._creds = creds
                self._save_credentials()
                return True
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                creds = None

        # No valid saved credentials, need to authenticate with client_id/client_secret
        if not client_id or not client_secret:
            logger.error("Client ID and Client Secret are required for initial authentication")
            return False

        # Build client config from provided credentials
        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }

        try:
            flow = InstalledAppFlow.from_client_config(
                client_config,
                SCOPES,
                redirect_uri=REDIRECT_URI
            )

            print(f"\n{'='*60}")
            print("Google Drive Authentication")
            print(f"{'='*60}")
            print("Opening browser for Google sign-in...")
            print("Client secret is used only for this authentication and is then discarded.")
            print(f"{'='*60}\n")

            self._creds = flow.run_local_server(port=8080)

            if self._creds:
                # Save ONLY the OAuth token, NOT the client secret
                self._save_credentials()
                print(f"Authentication successful!")
                print(f"OAuth token saved to: {self.token_path}")
                print("Client secret has been discarded from memory.")
                return True
            else:
                logger.error("No credentials received from Google")
                return False

        except Exception as e:
            logger.error(f"Failed to authenticate: {e}")
            return False

    def authenticate(self) -> bool:
        """Authenticate with Google Drive using saved OAuth token.
        This method uses only the saved token and does NOT require client_id/client_secret.
        """
        creds = self._load_credentials()

        if creds and creds.valid:
            self._creds = creds
            return True

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._creds = creds
                self._save_credentials()
                return True
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                creds = None

        # No valid saved credentials
        logger.error("No saved OAuth token found. Please authenticate with Google Cloud credentials first.")
        return False

    def _get_service(self):
        """Get or create Google Drive service"""
        if self._service is None:
            if not self._creds:
                if not self.authenticate():
                    raise Exception("Not authenticated with Google Drive")
            self._service = build('drive', 'v3', credentials=self._creds)
        return self._service

    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        # Try to load saved credentials first
        if not self._creds:
            self._creds = self._load_credentials()
        
        # Check if we have valid credentials
        if self._creds and self._creds.valid:
            return True
        
        # Try to refresh if expired but have refresh token
        if self._creds and self._creds.expired and self._creds.refresh_token:
            try:
                self._creds.refresh(Request())
                self._save_credentials()
                return True
            except Exception as e:
                logger.warning(f"Failed to refresh credentials: {e}")
        
        # If we have credentials but they're not valid, we're still "authenticated" 
        # because we can try to refresh or re-authenticate
        if self._creds:
            return True
            
        return False

    def upload_file(self, file_path: str, file_name: Optional[str] = None, folder_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to Google Drive"""
        try:
            service = self._get_service()
            file_name = file_name or os.path.basename(file_path)

            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [str(folder_id)]

            media = MediaFileUpload(file_path, resumable=True)

            file = service.files().create(body=file_metadata, media_body=media, fields='id,name,webViewLink,createdTime').execute()
            logger.info(f"Uploaded file: {file_name} (ID: {file.get('id')})")

            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'created_time': file.get('createdTime')
            }
        except HttpError as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def upload_content(self, content: str, file_name: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload string content to Google Drive as a file"""
        try:
            service = self._get_service()

            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [str(folder_id)]

            media = MediaIoBaseUpload(BytesIO(content.encode('utf-8')), resumable=True, mimetype='application/json')

            file = service.files().create(body=file_metadata, media_body=media, fields='id, name, webViewLink, createdTime').execute()
            logger.info(f"Uploaded content: {file_name} (ID: {file.get('id')})")

            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'created_time': file.get('createdTime')
            }
        except HttpError as e:
            logger.error(f"Failed to upload content: {e}")
            raise

    def list_files(self, folder_id: Optional[str] = None, file_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in Google Drive, optionally in a specific folder"""
        try:
            service = self._get_service()

            query = "trashed = false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            if file_name:
                query += f" and name = '{file_name}'"

            results = service.files().list(q=query, fields='files(id, name, webViewLink, createdTime, modifiedTime)').execute()
            return results.get('files', [])
        except HttpError as e:
            logger.error(f"Failed to list files: {e}")
            raise

    def download_file(self, file_id: str) -> bytes:
        """Download a file from Google Drive by ID"""
        try:
            service = self._get_service()
            request = service.files().get_media(fileId=file_id)
            file = service.files().get(fields='name').execute()

            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            logger.info(f"Downloaded file: {file.get('name')}")
            return fh.getvalue()
        except HttpError as e:
            logger.error(f"Failed to download file: {e}")
            raise

    def get_file_content(self, file_id: str) -> str:
        """Download file content as string"""
        content = self.download_file(file_id)
        return content.decode('utf-8')

    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive"""
        try:
            service = self._get_service()
            service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file: {file_id}")
            return True
        except HttpError as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a folder in Google Drive"""
        try:
            service = self._get_service()

            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [str(parent_id)]

            file = service.files().create(body=file_metadata, fields='id, name, webViewLink').execute()
            logger.info(f"Created folder: {folder_name} (ID: {file.get('id')})")

            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'web_view_link': file.get('webViewLink')
            }
        except HttpError as e:
            logger.error(f"Failed to create folder: {e}")
            raise

    def find_folder(self, folder_name: str) -> Optional[Dict[str, Any]]:
        """Find a folder by name"""
        try:
            service = self._get_service()
            results = service.files().list(
                q=f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
                fields='files(id, name, webViewLink)'
            ).execute()
            files = results.get('files', [])
            return files[0] if files else None
        except HttpError as e:
            logger.error(f"Failed to find folder: {e}")
            return None
