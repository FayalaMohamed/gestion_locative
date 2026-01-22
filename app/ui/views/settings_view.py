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

        progress_group = QGroupBox("Progression")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)

        progress_group.setLayout(progress_layout)
        self.layout().addWidget(progress_group)

        self.layout().addStretch()

    def setup_connections(self):
        self.btn_export.clicked.connect(self.on_export)
        self.btn_import.clicked.connect(self.on_import)

    def on_export(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les données",
            f"gestion_locative_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "Fichiers JSON (*.json)"
        )

        if not file_path:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Exportation en cours...")

        QTimer.singleShot(100, lambda: self._do_export(file_path))

    def _do_export(self, file_path: str):
        try:
            data_service = DataService()
            data = data_service.export_all()

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            self.progress_bar.setValue(100)
            self.status_label.setText("Exportation terminée!")

            QMessageBox.information(
                self,
                "Succès",
                f"Données exportées avec succès vers:\n{file_path}"
            )
        except Exception as e:
            self.status_label.setText("Erreur lors de l'exportation")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'exportation:\n{str(e)}"
            )
        finally:
            self.progress_bar.setVisible(False)

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

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Importation en cours...")

        QTimer.singleShot(100, lambda: self._do_import(file_path))

    def _do_import(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data_service = DataService()
            data_service.import_all(data)

            self.progress_bar.setValue(100)
            self.status_label.setText("Importation terminée!")

            QMessageBox.information(
                self,
                "Succès",
                "Données importées avec succès!\n\n"
                "Veuillez redémarrer l'application pour voir les changements."
            )

            if self.parent_window:
                self.parent_window.views.get("dashboard").load_data()
        except json.JSONDecodeError as e:
            self.status_label.setText("Erreur: fichier JSON invalide")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Fichier JSON invalide:\n{str(e)}"
            )
        except Exception as e:
            self.status_label.setText("Erreur lors de l'importation")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'importation:\n{str(e)}"
            )
        finally:
            self.progress_bar.setVisible(False)
