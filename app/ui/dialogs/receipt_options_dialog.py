#!/usr/bin/env python
"""
Receipt Options Dialog for selecting company name and signature
"""
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QFileDialog, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon

from app.utils.config import Config


class ReceiptOptionsDialog(QDialog):
    """Dialog to choose company name and signature for receipt generation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options du reçu")
        self.setMinimumWidth(500)
        self.resize(500, 400)
        
        self.selected_company_name = None
        self.selected_signature_path = None
        
        self.config = Config()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Company Name Section
        company_group = QGroupBox("Nom de l'émetteur du reçu")
        company_layout = QFormLayout()
        
        # Combo box for existing names
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        self.name_combo.setInsertPolicy(QComboBox.NoInsert)
        self.name_combo.setMinimumWidth(300)
        company_layout.addRow("Nom:", self.name_combo)
        
        # Info label
        self.name_info = QLabel("Sélectionnez un nom existant ou tapez un nouveau")
        self.name_info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        company_layout.addRow("", self.name_info)
        
        company_group.setLayout(company_layout)
        layout.addWidget(company_group)
        
        # Signature Section
        signature_group = QGroupBox("Signature")
        signature_layout = QVBoxLayout()
        
        # Signature list
        self.signature_list = QListWidget()
        self.signature_list.setMaximumHeight(100)
        signature_layout.addWidget(QLabel("Signatures disponibles:"))
        signature_layout.addWidget(self.signature_list)
        
        # Signature preview
        self.signature_preview = QLabel("Aucune signature sélectionnée")
        self.signature_preview.setAlignment(Qt.AlignCenter)
        self.signature_preview.setMinimumHeight(80)
        self.signature_preview.setStyleSheet("border: 1px solid #bdc3c7; background-color: #ecf0f1;")
        signature_layout.addWidget(QLabel("Aperçu:"))
        signature_layout.addWidget(self.signature_preview)
        
        # Signature buttons
        sig_buttons_layout = QHBoxLayout()
        
        self.btn_add_signature = QPushButton("Importer une signature...")
        self.btn_add_signature.setStyleSheet("background-color: #9b59b6; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        sig_buttons_layout.addWidget(self.btn_add_signature)
        
        self.btn_delete_signature = QPushButton("Supprimer")
        self.btn_delete_signature.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        self.btn_delete_signature.setEnabled(False)
        sig_buttons_layout.addWidget(self.btn_delete_signature)
        
        sig_buttons_layout.addStretch()
        signature_layout.addLayout(sig_buttons_layout)
        
        signature_group.setLayout(signature_layout)
        layout.addWidget(signature_group)
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px 24px; border-radius: 4px; border: none;")
        buttons_layout.addWidget(self.btn_cancel)
        
        self.btn_generate = QPushButton("Générer le reçu")
        self.btn_generate.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 24px; border-radius: 4px; border: none;")
        buttons_layout.addWidget(self.btn_generate)
        
        layout.addLayout(buttons_layout)
        
        # Connect signals
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_generate.clicked.connect(self.on_generate)
        self.btn_add_signature.clicked.connect(self.on_import_signature)
        self.btn_delete_signature.clicked.connect(self.on_delete_signature)
        self.signature_list.currentRowChanged.connect(self.on_signature_selected)
        self.name_combo.currentTextChanged.connect(self.on_name_changed)
        
    def load_data(self):
        """Load company names and signatures from config"""
        # Load company names
        names = self.config.get_company_names()
        self.name_combo.clear()
        for name in names:
            self.name_combo.addItem(name)
        
        # Set first name as default if available
        if names:
            self.name_combo.setCurrentIndex(0)
        
        # Load signatures
        self._load_signatures()
    
    def _load_signatures(self):
        """Load signatures into the list"""
        self.signature_list.clear()
        signatures = self.config.get_signatures()
        
        # Add "No signature" option
        item = QListWidgetItem("Aucune signature")
        item.setData(Qt.UserRole, '')
        self.signature_list.addItem(item)
        
        for i, sig in enumerate(signatures):
            item = QListWidgetItem(sig.get('name', f"Signature {i+1}"))
            item.setData(Qt.UserRole, sig.get('path', ''))
            item.setData(Qt.UserRole + 1, i)  # Store index for deletion
            self.signature_list.addItem(item)
        
        # Select first item (no signature) by default
        self.signature_list.setCurrentRow(0)
        self.on_signature_selected(0)
    
    def on_signature_selected(self, row):
        """Handle signature selection"""
        if row < 0:
            self.btn_delete_signature.setEnabled(False)
            self.signature_preview.setText("Aucune signature sélectionnée")
            return
        
        item = self.signature_list.item(row)
        path = item.data(Qt.UserRole)
        index = item.data(Qt.UserRole + 1)
        
        # Enable delete button only for actual signatures (not "no signature" option)
        self.btn_delete_signature.setEnabled(index is not None)
        
        # Show preview
        if path and Path(path).exists():
            try:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.signature_preview.width() - 20,
                        self.signature_preview.height() - 20,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.signature_preview.setPixmap(scaled_pixmap)
                else:
                    self.signature_preview.setText("Format d'image non supporté")
            except Exception as e:
                self.signature_preview.setText(f"Erreur: {str(e)}")
        else:
            self.signature_preview.setText("Aucune signature sélectionnée" if not path else "Fichier introuvable")
    
    def on_name_changed(self, text):
        """Handle company name change"""
        self.selected_company_name = text.strip()
    
    def on_import_signature(self):
        """Import a new signature"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer une signature",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if not file_path:
            return
        
        # Generate a name for the signature
        file_name = Path(file_path).stem
        name, ok = self._show_input_dialog(
            "Nom de la signature",
            "Donnez un nom à cette signature:",
            file_name
        )
        
        if ok and name:
            self.config.add_signature(name.strip(), file_path)
            self._load_signatures()
            
            # Select the newly added signature
            for i in range(self.signature_list.count()):
                item = self.signature_list.item(i)
                if item.data(Qt.UserRole) == file_path:
                    self.signature_list.setCurrentRow(i)
                    break
    
    def _show_input_dialog(self, title, label, default_text=""):
        """Show a simple input dialog"""
        from PySide6.QtWidgets import QInputDialog
        return QInputDialog.getText(self, title, label, text=default_text)
    
    def on_delete_signature(self):
        """Delete the selected signature"""
        row = self.signature_list.currentRow()
        if row < 0:
            return
        
        item = self.signature_list.item(row)
        index = item.data(Qt.UserRole + 1)
        
        if index is None:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cette signature?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.remove_signature(index)
            self._load_signatures()
    
    def on_generate(self):
        """Validate and accept"""
        name = self.name_combo.currentText().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation", "Veuillez entrer un nom pour l'émetteur du reçu")
            return
        
        self.selected_company_name = name
        
        # Get selected signature path
        row = self.signature_list.currentRow()
        if row >= 0:
            item = self.signature_list.item(row)
            self.selected_signature_path = item.data(Qt.UserRole)
        else:
            self.selected_signature_path = ''
        
        # Add name to history if new
        existing_names = self.config.get_company_names()
        if name not in existing_names:
            self.config.add_company_name(name)
        
        self.accept()
    
    def get_options(self):
        """Return selected options"""
        return {
            'company_name': self.selected_company_name,
            'signature_path': self.selected_signature_path
        }
