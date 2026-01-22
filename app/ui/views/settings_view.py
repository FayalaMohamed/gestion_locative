#!/usr/bin/env python
"""
Settings view for data management (export/import)
"""
import json
from datetime import datetime
from typing import Any, Dict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox, QProgressBar,
    QTextEdit
)
from PySide6.QtCore import Qt, QTimer

from app.ui.views.base_view import BaseView
from app.services.data_service import DataService
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

        self.layout().addStretch()

    def setup_connections(self):
        self.btn_export.clicked.connect(self.on_export)
        self.btn_import.clicked.connect(self.on_import)
        self.btn_import_signature.clicked.connect(self.on_import_signature)
        self.btn_clear_signature.clicked.connect(self.on_clear_signature)
        self._load_signature_status()

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
