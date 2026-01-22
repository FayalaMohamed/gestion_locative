#!/usr/bin/env python
"""
Settings view for data management (export/import)
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox, QProgressBar,
    QTextEdit, QLineEdit
)
from PySide6.QtCore import Qt, QTimer

from app.ui.views.base_view import BaseView
from app.services.data_service import DataService
from app.services.backup_service import BackupService
from app.utils.config import Config


class SettingsView(BaseView):
    def setup_ui(self):
        super().setup_ui()

        header_layout = QHBoxLayout()

        title = QLabel("Paramètres")
        title.setObjectName("view_title")
        header_layout.addWidget(title)

        header_layout.addStretch()
        self.layout().addLayout(header_layout)

        export_group = QGroupBox("Exportation des données")
        export_layout = QFormLayout()

        self.btn_export = QPushButton("Exporter tout en JSON...")
        self.btn_export.setStyleSheet("background-color: #3498db; color: white; padding: 12px 24px; border-radius: 4px; border: none;")
        export_layout.addRow("", self.btn_export)

        self.export_info = QLabel("Exporte toutes les données de l'application vers un fichier JSON")
        self.export_info.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        export_layout.addRow("", self.export_info)

        export_group.setLayout(export_layout)
        self.layout().addWidget(export_group)

        import_group = QGroupBox("Importation des données")
        import_layout = QFormLayout()

        self.btn_import = QPushButton("Importer depuis JSON...")
        self.btn_import.setStyleSheet("background-color: #27ae60; color: white; padding: 12px 24px; border-radius: 4px; border: none;")
        import_layout.addRow("", self.btn_import)

        self.import_warning = QLabel("Attention: L'importation remplacera toutes les données existantes!")
        self.import_warning.setStyleSheet("color: #e74c3c; font-size: 13px;")
        import_layout.addRow("", self.import_warning)

        import_group.setLayout(import_layout)
        self.layout().addWidget(import_group)

        signature_group = QGroupBox("Signature sur les reçus")
        signature_layout = QFormLayout()

        self.btn_import_signature = QPushButton("Importer une signature...")
        self.btn_import_signature.setStyleSheet("background-color: #9b59b6; color: white; padding: 12px 24px; border-radius: 4px; border: none;")
        signature_layout.addRow("", self.btn_import_signature)

        self.signature_path_label = QLabel("Aucune signature importée")
        self.signature_path_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        signature_layout.addRow("", self.signature_path_label)

        self.btn_clear_signature = QPushButton("Supprimer la signature")
        self.btn_clear_signature.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        self.btn_clear_signature.setEnabled(False)
        signature_layout.addRow("", self.btn_clear_signature)

        signature_group.setLayout(signature_layout)
        self.layout().addWidget(signature_group)

        google_drive_group = QGroupBox("Google Drive - Sauvegarde Cloud")
        google_drive_layout = QFormLayout()

        self.google_drive_status = QLabel("Non connecté")
        self.google_drive_status.setStyleSheet("color: #e74c3c; font-size: 13px;")
        google_drive_layout.addRow("Statut:", self.google_drive_status)

        # Google Cloud Credentials section
        credentials_label = QLabel("Identifiants Google Cloud:")
        credentials_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        google_drive_layout.addRow("", credentials_label)

        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Entrez votre Client ID Google Cloud")
        google_drive_layout.addRow("Client ID:", self.client_id_input)

        self.client_secret_input = QLineEdit()
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        self.client_secret_input.setPlaceholderText("Entrez votre Client Secret Google Cloud")
        google_drive_layout.addRow("Client Secret:", self.client_secret_input)

        self.btn_save_credentials = QPushButton("Enregistrer les identifiants")
        self.btn_save_credentials.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        google_drive_layout.addRow("", self.btn_save_credentials)

        self.btn_google_auth = QPushButton("Se connecter à Google Drive...")
        self.btn_google_auth.setStyleSheet("background-color: #4285f4; color: white; padding: 12px 24px; border-radius: 4px; border: none;")
        google_drive_layout.addRow("", self.btn_google_auth)

        self.btn_google_backup = QPushButton("Sauvegarder sur Google Drive")
        self.btn_google_backup.setStyleSheet("background-color: #27ae60; color: white; padding: 12px 24px; border-radius: 4px; border: none;")
        self.btn_google_backup.setEnabled(False)
        google_drive_layout.addRow("", self.btn_google_backup)

        self.btn_google_list = QPushButton("Voir les sauvegardes cloud")
        self.btn_google_list.setStyleSheet("background-color: #3498db; color: white; padding: 12px 24px; border-radius: 4px; border: none;")
        self.btn_google_list.setEnabled(False)
        google_drive_layout.addRow("", self.btn_google_list)

        self.google_info = QLabel("Connectez-vous à Google Drive pour sauvegarder et restaurer vos données dans le cloud")
        self.google_info.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        google_drive_layout.addRow("", self.google_info)

        google_drive_group.setLayout(google_drive_layout)
        self.layout().addWidget(google_drive_group)

        self.layout().addStretch()

    def setup_connections(self):
        self.btn_export.clicked.connect(self.on_export)
        self.btn_import.clicked.connect(self.on_import)
        self.btn_import_signature.clicked.connect(self.on_import_signature)
        self.btn_clear_signature.clicked.connect(self.on_clear_signature)
        self.btn_save_credentials.clicked.connect(self.on_save_credentials)
        self.btn_google_auth.clicked.connect(self.on_google_auth)
        self.btn_google_backup.clicked.connect(self.on_google_backup)
        self.btn_google_list.clicked.connect(self.on_google_list)
        self._load_signature_status()
        self._update_google_drive_status()

    def on_export(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les données",
            f"gestion_locative_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "Fichiers JSON (*.json)"
        )

        if not file_path:
            return

        self._do_export(file_path)

    def _do_export(self, file_path: str):
        try:
            data_service = DataService()
            data = data_service.export_all()

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            QMessageBox.information(
                self,
                "Succès",
                f"Données exportées avec succès vers:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'exportation:\n{str(e)}"
            )
        finally:
            pass

    def on_import(self):
        reply = QMessageBox.warning(
            self,
            "Confirmation",
            "Attention: L'importation remplacera toutes les données existantes.\n\n"
            "Êtes-vous sûr de vouloir continuer?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer les données",
            "",
            "Fichiers JSON (*.json)"
        )

        if not file_path:
            return

        self._do_import(file_path)

    def _do_import(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data_service = DataService()
            data_service.import_all(data)

            QMessageBox.information(
                self,
                "Succès",
                "Données importées avec succès!\n\n"
                "Veuillez redémarrer l'application pour voir les changements."
            )

            if self.parent_window:
                self.parent_window.views.get("dashboard").load_data()
        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'importation:\n{str(e)}"
            )

    def _load_signature_status(self):
        import os
        config = Config.get_instance()
        signature_path = config.get('receipts', 'signature_path', default='')
        if signature_path and os.path.exists(signature_path):
            self.signature_path_label.setText(signature_path)
            self.signature_path_label.setStyleSheet("color: #27ae60; font-size: 13px;")
            self.btn_clear_signature.setEnabled(True)
        else:
            self.signature_path_label.setText("Aucune signature importée")
            self.signature_path_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
            self.btn_clear_signature.setEnabled(False)

    def on_import_signature(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer une signature",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        config = Config.get_instance()
        config.set(file_path, 'receipts', 'signature_path')
        config.save_config()

        self._load_signature_status()

        QMessageBox.information(
            self,
            "Succès",
            "Signature importée avec succès!\nElle sera affichée sur les nouveaux reçus."
        )

    def on_clear_signature(self):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer la signature?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        config = Config.get_instance()
        config.set('', 'receipts', 'signature_path')
        config.save_config()

        self._load_signature_status()

        QMessageBox.information(
            self,
            "Succès",
            "Signature supprimée avec succès."
        )

    def on_save_credentials(self):
        """Authenticate with Google Cloud credentials.
        Credentials are used only for authentication and then discarded from memory.
        Only the OAuth token is saved for future use.
        """
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()

        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "Identifiants incomplets",
                "Veuillez saisir à la fois le Client ID et le Client Secret."
            )
            return

        self.btn_save_credentials.setEnabled(False)
        self.btn_save_credentials.setText("Authentification en cours...")

        QTimer.singleShot(100, lambda: self._do_authenticate(client_id, client_secret))

    def _do_authenticate(self, client_id: str, client_secret: str):
        """Perform the actual authentication with credentials"""
        try:
            self.backup_service = BackupService()
            if self.backup_service.google_drive.authenticate_with_credentials(client_id, client_secret):
                # Clear the credential fields for security
                self.client_id_input.clear()
                self.client_secret_input.clear()

                QMessageBox.information(
                    self,
                    "Succès",
                    "Connexion à Google Drive établie avec succès!\n\n"
                    "Vos identifiants ont été utilisés uniquement pour cette authentification.\n"
                    "Seul le jeton OAuth a été enregistré pour les utilisations futures.\n\n"
                    "Vous pouvez maintenant sauvegarder et restaurer vos données."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Échec de la connexion à Google Drive.\n\n"
                    "Vérifiez que vos identifiants sont corrects."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la connexion:\n{str(e)}"
            )
        finally:
            self.btn_save_credentials.setEnabled(True)
            self.btn_save_credentials.setText("Enregistrer les identifiants")
            self._update_google_drive_status()

    def _update_google_drive_status(self):
        """Update Google Drive connection status"""
        self.backup_service = BackupService()

        auth_status = self.backup_service.is_authenticated()

        if auth_status:
            self.google_drive_status.setText("Connecte a Google Drive")
            self.google_drive_status.setStyleSheet("color: #27ae60; font-size: 13px;")
            self.btn_google_backup.setEnabled(True)
            self.btn_google_list.setEnabled(True)
            self.btn_google_auth.setText("Reconnecter a Google Drive")
            self.btn_save_credentials.setText("Reauthentifier")
            self.google_info.setText("Vous pouvez maintenant sauvegarder et restaurer vos donnees sur Google Drive.\nLes identifiants ne sont pas stockes - seul le jeton OAuth est enregistre.")
            self.client_id_input.setEnabled(False)
            self.client_secret_input.setEnabled(False)
        else:
            self.google_drive_status.setText("Non connecte")
            self.google_drive_status.setStyleSheet("color: #e74c3c; font-size: 13px;")
            self.btn_google_backup.setEnabled(False)
            self.btn_google_list.setEnabled(False)
            self.btn_google_auth.setText("Se connecter a Google Drive...")
            self.btn_save_credentials.setText("Enregistrer les identifiants")
            self.google_info.setText("Entrez vos identifiants Google Cloud pour vous connecter.\nLes identifiants ne sont pas stockes sur le disque.")
            self.client_id_input.setEnabled(True)
            self.client_secret_input.setEnabled(True)



    def on_google_auth(self):
        """Re-authenticate with Google Drive using saved token"""
        self.btn_google_auth.setEnabled(False)
        self.btn_google_auth.setText("Connexion en cours...")

        QTimer.singleShot(100, self._do_reauthenticate)

    def _do_reauthenticate(self):
        """Re-authenticate using saved OAuth token"""
        try:
            self.backup_service = BackupService()
            if self.backup_service.google_drive.authenticate():
                QMessageBox.information(
                    self,
                    "Succès",
                    "Connexion à Google Drive rétablie avec succès!\n\n"
                    "Vous pouvez maintenant sauvegarder et restaurer vos données."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Échec de la reconnexion à Google Drive.\n\n"
                    "Le jeton OAuth a peut-être expiré ou été révoqué.\n"
                    "Veuillez vous authentifier à nouveau avec vos identifiants."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la reconnexion:\n{str(e)}"
            )
        finally:
            self.btn_google_auth.setEnabled(True)
            self.btn_google_auth.setText("Reconnecter a Google Drive")
            self._update_google_drive_status()

    def on_google_backup(self):
        """Backup database to Google Drive"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir créer une sauvegarde sur Google Drive?\n\n"
            "Cette action exportera toutes les données de l'application.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.btn_google_backup.setEnabled(False)
        self.btn_google_backup.setText("Sauvegarde en cours...")

        QTimer.singleShot(100, self._do_google_backup)

    def _do_google_backup(self):
        try:
            self.backup_service = BackupService()
            result = self.backup_service.backup_to_google_drive()

            if result['success']:
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Sauvegarde créée avec succès sur Google Drive!\n\n"
                    f"Fichier: {result['file_name']}\n"
                    f"Date: {result['backup_date']}\n\n"
                    f"Vous pouvez voir ce fichier dans le dossier 'Gestion Locative Pro Backups' sur votre Google Drive."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Échec de la sauvegarde:\n{result.get('error', 'Erreur inconnue')}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la sauvegarde:\n{str(e)}"
            )
        finally:
            self.btn_google_backup.setEnabled(True)
            self.btn_google_backup.setText("Sauvegarder sur Google Drive")

    def on_google_list(self):
        """List Google Drive backups"""
        self.btn_google_list.setEnabled(False)
        self.btn_google_list.setText("Chargement...")

        QTimer.singleShot(100, self._do_google_list)

    def _do_google_list(self):
        try:
            self.backup_service = BackupService()
            backups = self.backup_service.list_google_drive_backups()

            if not backups:
                QMessageBox.information(
                    self,
                    "Sauvegardes",
                    "Aucune sauvegarde trouvée sur Google Drive.\n\n"
                    "Créez votre première sauvegarde en cliquant sur 'Sauvegarder sur Google Drive'."
                )
            else:
                backup_text = "Sauvegardes disponibles dans 'Gestion Locative Pro Backups':\n\n"
                for i, backup in enumerate(backups, 1):
                    from datetime import datetime
                    created_time = backup.get('created_time', '')
                    if created_time:
                        try:
                            dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                            created_time = dt.strftime('%d/%m/%Y %H:%M')
                        except:
                            pass
                    backup_text += f"{i}. {backup['name']}\n   Date: {created_time}\n\n"

                QMessageBox.information(
                    self,
                    "Sauvegardes Cloud",
                    backup_text
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la récupération des sauvegardes:\n{str(e)}"
            )
        finally:
            self.btn_google_list.setEnabled(True)
            self.btn_google_list.setText("Voir les sauvegardes cloud")
